# Status projektu

Stan na 28.10.2026.

Cel projektu został ograniczony do planowania poziomej trasy UAV od punktu A do
punktu B na podstawie danych z LiDAR-u. Wcześniejszy kierunek obejmujący model
dynamiki lotu, środowisko RL i self-play nie należy do bieżącego zakresu.

## Ustalone założenia

- planowanie odbywa się w 2D;
- konfiguracja i dynamika UAV są pomijane;
- znana siatka wysokości budynków może posłużyć do planowania przed lotem;
- NetworkX A* jest wybraną metodą początkowego planowania na grafie 2D;
- A* na lokalnej siatce zajętości jest wybraną pierwszą metodą reaktywnego
  ponownego planowania;
- planowanie początkowe jest opcjonalne i wymienne;
- planowanie początkowe wymaga geometrii i włączonego `preplan`;
- CLI `--preplan` / `--no-preplan` ma pierwszeństwo przed konfiguracją YAML;
- lokalne dane LiDAR-u mogą zmienić trasę zaplanowaną z mapy;
- planer dynamiczny omija nowe przeszkody i próbuje bezpiecznie wrócić na trasę;
- brak możliwości powrotu na trasę nie wyłącza dynamicznego planowania do celu;
- lot bez mapy i bez trasy początkowej musi być obsługiwany;
- LiDAR ma konfigurowalną liczbę promieni, częstotliwość i zasięg;
- wartości początkowe to jeden promień, 10 Hz i 10 m;
- minimalna odległość od przeszkody jest parametrem;
- wynik stanowi lista punktów kontrolnych prowadzących do celu;
- dodatkowe źródła mapy mają być możliwe bez zmiany interfejsu planera.

## Stan implementacji

Usunięto wcześniejsze moduły dynamiki lotu, treningu, agentów i środowisk RL
oraz konfigurację treningu i katalog checkpointów. Usunięto zależności od
Torch, Gymnasium, JSBSim, SKRL i Matplotlib oraz konfigurację indeksów
CPU/CUDA.

Nowa struktura obejmuje:

- instalowalny pakiet `src` bez dodatkowego katalogu nadrzędnego;
- walidowaną konfigurację YAML z parametrami LiDAR-u, siatki i marginesu;
- ustawienie `preplan`, jego nadpisanie przez CLI i warunek dostępnej geometrii;
- polecenie `uav-planner` do sprawdzania i wyświetlania konfiguracji;
- kontrakt `GlobalPlanner` niezależny od konkretnej biblioteki i transportu;
- osobne granice modułów `planning`, `mapping` i `integration`;
- testy konfiguracji i jej walidacji.

NetworkX i PyYAML zastępują `extremitypathfinder` oraz konfigurację TOML.
Nie ma jeszcze adaptera planera NetworkX, mapowania LiDAR-u, lokalnego A*, koordynatora
misji ani integracji z symulatorem. Polecenie konfiguracyjne nie wyznacza tras.
Rozdzielczość siatki i margines bezpieczeństwa wymagają późniejszej kalibracji.
Najkrótsza trasa oznacza optimum w dostępnym grafie aktualnego modelu, nie
gwarancję globalnego optimum w nieznanym środowisku ani w ciągłej geometrii.

## Następny krok

Po otrzymaniu symulatora Three.js trzeba ustalić minimalny kontrakt komunikacji:

- układ współrzędnych i jednostki;
- format pozycji, orientacji i celu;
- format siatki wysokości budynków oraz poziom lotu;
- znaczenie częstotliwości obrotu LiDAR-u;
- format, kąty i znaczniki czasu próbek;
- sposób przekazywania punktów kontrolnych;
- zachowanie dla braku trasy, utraty danych i osiągnięcia celu.

Dopiero wtedy należy wybrać miejsce uruchomienia planera i zaimplementować
najmniejszą integrację bez zbędnego pośrednictwa między Pythonem a TypeScriptem.
Pierwszy pionowy zakres funkcjonalny powinien obejmować opcjonalny plan globalny,
wykrycie nieoczekiwanej przeszkody i bezpieczny lokalny objazd.
