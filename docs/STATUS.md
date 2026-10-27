# Status projektu

Stan na 27.10.2026.

Cel projektu został ograniczony do planowania poziomej trasy UAV od punktu A do
punktu B na podstawie danych z LiDAR-u. Wcześniejszy kierunek obejmujący model
dynamiki lotu, środowisko RL i self-play nie należy do bieżącego zakresu.

## Ustalone założenia

- planowanie odbywa się w 2D;
- konfiguracja i dynamika UAV są pomijane;
- znana siatka wysokości budynków może posłużyć do planowania przed lotem;
- `extremitypathfinder` jest wybraną implementacją początkowego planera 2D;
- A* na lokalnej siatce zajętości jest wybraną pierwszą metodą reaktywnego
  ponownego planowania;
- planowanie początkowe jest opcjonalne i wymienne;
- lokalne dane LiDAR-u mogą zmienić trasę zaplanowaną z mapy;
- lot bez mapy i bez trasy początkowej musi być obsługiwany;
- LiDAR ma konfigurowalną liczbę promieni, częstotliwość i zasięg;
- wartości początkowe to jeden promień, 10 Hz i 10 m;
- minimalna odległość od przeszkody jest parametrem;
- wynik stanowi lista punktów kontrolnych prowadzących do celu;
- dodatkowe źródła mapy mają być możliwe bez zmiany interfejsu planera.

## Stan implementacji

Repozytorium zawiera scaffold poprzedniego podejścia do dynamiki lotu i RL.
Nie ma jeszcze implementacji planera globalnego, mapowania LiDAR-u, lokalnego
planowania ani integracji z symulatorem. `extremitypathfinder` nie został
jeszcze dodany do zależności. Istniejących modułów nie należy traktować jako
architektury nowego planera.

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
