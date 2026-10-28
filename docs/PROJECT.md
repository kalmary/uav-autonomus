# Planowanie poziomej trasy UAV

## 1. Cel projektu

Celem projektu jest hybrydowe planowanie globalne i lokalne bezkolizyjnej trasy
lotu poziomego od punktu A do punktu B. Jeżeli geometria świata jest znana i
włączono planowanie początkowe, trasa globalna jest wyznaczana przed lotem.
Podczas lotu dane z LiDAR-u służą do
sprawdzania tej trasy i tworzenia lokalnych objazdów, gdy rzeczywiste przeszkody
różnią się od mapy. Lot bez mapy i bez planu początkowego również musi być
możliwy.

Pierwsza wersja nie modeluje konfiguracji ani dynamiki UAV. Pojazd jest
traktowany jako punkt poruszający się w płaszczyźnie 2D. Optymalizacja dotyczy
długości geometrycznej trasy. Planowanie najszybszej trasy będzie możliwe
dopiero po wprowadzeniu ograniczeń prędkości, przyspieszenia i skrętu.

## 2. Dane wejściowe i wynik

Minimalne dane wejściowe:

- bieżąca pozycja UAV `(x, y)` i orientacja w stałym układzie współrzędnych;
- punkt docelowy `(x, y)`;
- próbki LiDAR-u: czas, kąt promienia, zmierzona odległość i zasięg maksymalny;
- opcjonalna siatka wysokości budynków oraz wysokość lotu;
- minimalna dopuszczalna odległość od przeszkody.

Początkowy model LiDAR-u ma jeden obracający się promień, częstotliwość 10 Hz i
zasięg 10 m. Liczba promieni, częstotliwość i zasięg są parametrami, a nie
stałymi algorytmu. W przyszłości wejście może zostać rozszerzone o skan 3D.

Wynik planera zawiera:

- uporządkowane punkty kontrolne `(x, y)`;
- stan planowania: trasa znaleziona, eksploracja, brak trasy albo osiągnięcie
  celu.

## 3. Rozwiązanie: planer hybrydowy globalny–lokalny

Planer globalny jest opcjonalny i korzysta z NetworkX A*. Wymaga jednocześnie
dostępnej geometrii świata i włączonego ustawienia `preplan`. Argumenty CLI
`--preplan` i `--no-preplan` mają pierwszeństwo przed ustawieniem YAML.
Bez argumentu CLI używana jest wartość z pliku, a dla pominiętego ustawienia
wartość domyślna `true`. Brak geometrii, wyłączenie planowania początkowego
lub brak trasy początkowej oznacza przejście do samego planowania dynamicznego.

Komórki siatki budynków, których wysokość koliduje z poziomem lotu, są oznaczane
jako zajęte i powiększane o wymagany margines bezpieczeństwa. Na tej podstawie
tworzony jest graf bezkolizyjnych połączeń. Koszt krawędzi odpowiada długości
odcinka w metrach, a heurystyka A* jest odległością euklidesową. NetworkX
wyznacza najkrótszą trasę w tym grafie. Dla grafu siatkowego wynik zależy od
rozdzielczości i dopuszczonych połączeń; nie jest gwarancją geometrycznie
najkrótszej trasy w ciągłej płaszczyźnie. Połączenia po przekątnej i uproszczone
odcinki również muszą być sprawdzane pod kątem kolizji i marginesu.

Planer lokalny działa zawsze. Pierwszą implementacją jest A* na bieżącej siatce
zajętości budowanej z LiDAR-u. Sprawdza najbliższy fragment trasy globalnej i w
razie różnicy wyznacza lokalny objazd, a wynik upraszcza do punktów kontrolnych.
Po minięciu przeszkody wraca do dalszej części trasy globalnej, jeżeli pozostaje
ona bezpieczna i osiągalna. Jeżeli nie może wrócić na trasę, kontynuuje
planowanie dynamiczne do celu zamiast blokować misję samym brakiem połączenia
z trasą referencyjną. Brak planu globalnego nie jest błędem: celem długoterminowym
jest wtedy punkt B, a postęp odbywa się przez punkty osiągalne w aktualnie
rozpoznanym obszarze.

Planowanie dynamiczne pozostaje aktywne przez cały lot, również podczas
korzystania z trasy utworzonej przez NetworkX. Nowa przeszkoda powoduje
aktualizację mapy i ponowne wyznaczenie bezpiecznego fragmentu. Celem jest
możliwie krótka bezkolizyjna trasa w aktualnym modelu świata, także bez planu
początkowego. Nieznane komórki nie potwierdzają bezpiecznego przejazdu:
eksploracja może prowadzić tylko do bezpiecznie osiągalnych punktów, a brak
takiego punktu oznacza brak trasy, nie punkt prowadzący przez przeszkodę.

Przepływ danych:

1. Opcjonalny planer globalny tworzy trasę referencyjną z mapy początkowej.
2. Adapter symulatora odbiera pozycję UAV, cel i próbki LiDAR-u.
3. Moduł mapowania aktualizuje lokalną reprezentację zajętości 2D.
4. Planer lokalny sprawdza trasę referencyjną lub kierunek do celu.
5. Bezpieczny fragment albo lokalny objazd jest zwracany jako punkty kontrolne.
6. Zmiana obserwowanej geometrii powoduje ponowne planowanie odpowiedniego
   fragmentu.

W nieznanym środowisku nie można zagwarantować globalnie najkrótszej trasy.
Planer wybiera najlepszą trasę na podstawie aktualnie dostępnych danych i
koryguje ją w trakcie lotu.

## 4. Granice modułów

Planer początkowy przyjmuje pozycję startową, cel i model świata, a zwraca trasę
referencyjną albo informację, że nie można jej utworzyć. Koordynator misji nie
może zależeć od NetworkX; zależność pozostaje wewnątrz konkretnej
implementacji. Dzięki temu można wyłączyć planowanie początkowe, zastąpić je
innym algorytmem 2D albo później dodać wariant 3D.

Planer lokalny nie zakłada, że mapa początkowa jest poprawna. Dane LiDAR-u mają
pierwszeństwo dla aktualnie obserwowanego obszaru. Jeżeli następny fragment
trasy nie jest bezpieczny i nie istnieje lokalny objazd, UAV nie otrzymuje
punktu prowadzącego przez przeszkodę.

Mapowanie i planowanie nie zależą od Three.js. Warstwa integracyjna odpowiada
wyłącznie za transport i konwersję komunikatów.

### Struktura pakietu

Kod znajduje się bezpośrednio w instalowalnym pakiecie `src`.
Podział odpowiedzialności:

- `config.py`: walidacja ustawień, odczyt konfiguracji YAML i warunek użycia
  planowania początkowego;
- `planning/base.py`: kontrakt opcjonalnego planera początkowego;
- `planning/`: przyszła implementacja planera globalnego i lokalnego A*;
- `mapping/`: przyszłe aktualizacje mapy z LiDAR-u i siatki wysokości;
- `integration/`: przyszły transport symulatora i konwersja komunikatów.

`GlobalPlanner.plan(start, goal)` zwraca krotkę punktów obejmującą początek i cel
albo `None`, gdy trasy nie ma. Dla identycznego początku i celu zwraca jeden
punkt. Współrzędne są podane w metrach w stałym kartezjańskim układzie świata.
Nieprawidłowe współrzędne mają powodować `ValueError`. Model świata z już
uwzględnionym marginesem bezpieczeństwa jest przekazywany podczas tworzenia
konkretnej implementacji, a nie przez interfejs koordynatora. Planer może zostać
pominięty; jego wynik pozostaje wyłącznie trasą referencyjną.

Konfiguracja początkowa znajduje się w `configs/planner.yaml`. Częstotliwość
LiDAR-u oznacza w niej pełne obroty na sekundę. Adapter będzie musiał jawnie
przeliczać częstotliwość i znaczniki czasu symulatora. Rozdzielczość siatki
0,25 m i margines 0,5 m są wartościami początkowymi do kalibracji, a nie
potwierdzonymi parametrami bezpieczeństwa.

Pakiety `mapping` i `integration` wyznaczają obecnie tylko granice modułów.
Nie definiują jeszcze formatu skanów ani protokołu symulatora. Polecenie
`uav-planner` służy wyłącznie do walidacji konfiguracji.

## 5. Etapy

1. Ustalić kontrakt komunikacji po otrzymaniu symulatora Three.js.
2. Zdefiniować mały kontrakt opcjonalnego planera początkowego.
3. Dodać implementację 2D opartą na NetworkX A* dla siatki budynków z warunkiem
   dostępnej geometrii i włączonego planowania początkowego.
4. Zaimplementować aktualizację lokalnej mapy z pozy i promieni LiDAR-u.
5. Dodać sprawdzanie trasy i lokalne objazdy, także bez planu początkowego.
6. Połączyć całość z symulatorem i zmierzyć czas ponownego planowania.
7. Dopiero na podstawie potrzeb dodać inny planer 2D, planer 3D lub
   optymalizację czasu przelotu.

## 6. Poza pierwszym zakresem

- model dynamiki i konfiguracji UAV;
- sterowanie silnikami lub powierzchniami sterowymi;
- uczenie przez wzmacnianie i self-play;
- planowanie pionowe i pełne 3D;
- gwarancja globalnie optymalnej trasy bez pełnej mapy;
- optymalizacja czasu lotu bez modelu ograniczeń ruchu.
