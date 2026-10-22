# Status: modele lotu do treningu

Stan na 22.10.2026. Wybór docelowego backendu dynamiki jest odłożony. Obecny
adapter JSBSim w `src/dynamics/jsbsim.py` pozwala uruchomić jeden model na CPU,
ale nie realizuje celu z `docs/PROJECT.md`: wielu środowisk aktualizowanych
jedną operacją PyTorch na CPU lub CUDA. Kilka osobnych instancji JSBSim można
uruchamiać równolegle na CPU, lecz nie daje to tensorowego kroku na GPU.

## Ostrzeżenia modelu F450

W paczce JSBSim 1.3.3 `load_model("F450")` zwraca sukces, ale wypisuje:

```text
YOU HAVE AN INCOMPATIBLE CFG FILE FOR THIS AIRCRAFT. RESULTS WILL BE UNPREDICTABLE !!
Current version needed is: 2.0
You have version: 3.0
Failed to tie property fcs/accelx/malfunction/fail_low to object methods
...
```

Pierwszy komunikat dotyczy **wersji formatu definicji samolotu**, a nie
niezgodności fizycznych czujników. Dołączony `F450.xml` deklaruje
`version="3.0"`; maintainer JSBSim potwierdził, że w tym miejscu powinno być
`2.0`. [Dyskusja JSBSim](https://github.com/JSBSim-Team/jsbsim/discussions/1183),
[definicja F450](https://github.com/JSBSim-Team/jsbsim/blob/master/aircraft/F450/F450.xml).

Druga grupa komunikatów dotyczy wiązania właściwości systemów. `F450.xml`
odwołuje się do `SensorImu.xml`, `SensorBaro.xml` i `SensorGps.xml`, których
nie ma w katalogu F450 dołączonym do wheel ani w
[katalogu F450 upstream](https://github.com/JSBSim-Team/jsbsim/tree/master/aircraft/F450).
W przytoczonej dyskusji użytkownik zgłosił, że po zmianie wersji na `2.0`
pozostałe błędy nadal występowały. Nie ustalono, czy brak tych plików jest
przyczyną komunikatów o wiązaniu. Sam fakt, że `run()` działa, nie potwierdza
poprawności trajektorii F450. Nie używać tego presetu jako zweryfikowanego
modelu treningowego ani wzorca kalibracyjnego przed sprawdzeniem jego fizyki.

To problem dołączonej konfiguracji F450, nie oznaka porzucenia JSBSim:
[wydanie 1.3.3 z 16.10.2026](https://pypi.org/project/jsbsim/) zawiera koła
dla Pythona 3.14 na macOS i Linuksie.

## Obejścia do rozważenia później

1. Zachować JSBSim do małych przebiegów referencyjnych samolotu klasycznego
   (`c172p`) i ewentualnie uruchamiać osobne instancje CPU. Nie przenosić go do
   pętli treningowej GPU.
2. Dla F450 przygotować wersjonowaną kopię definicji poza `.venv`, poprawić
   deklarację wersji i rozwiązać brakujące/niezwiązane systemy. Potem porównać
   start, zawis, reakcje na sterowanie i jednostki z udokumentowanymi danymi.
   Sama edycja `version="3.0"` nie jest wystarczającą naprawą.
3. Do właściwego treningu wybrać backend, którego stan i krok są batched
   tensorami PyTorch; modele quadcoptera i samolotu powinny mieć jawny
   kontrakt stanu, sterowania, jednostek i resetu.

## Przegląd dostępnych narzędzi i ich aktualności

| Narzędzie | Aktualność i zakres | Ograniczenie dla tego repo |
| --- | --- | --- |
| [JSBSim](https://pypi.org/project/jsbsim/) | Aktywne; 1.3.3 z 16.10.2026. Gotowe modele samolotów, w tym `c172p`. | Jeden `FGFDMExec` odpowiada pojedynczej symulacji CPU; dołączony F450 wymaga naprawy i walidacji. |
| [RotorPy](https://pypi.org/project/rotorpy/) | Aktywne; 3.0.0 z 07.09.2026. Ma [batched symulację multirotorów na CPU/GPU](https://github.com/spencerfolk/rotorpy#batched-simulations). | Nie dostarcza modelu samolotu klasycznego. Jego [zależności bazowe](https://github.com/spencerfolk/rotorpy/blob/main/pyproject.toml) zawierają `matplotlib`, `pandas` i `cvxopt`, więc wizualizacja trafiłaby także do środowiska runtime. Wymaga sprawdzenia na Pythonie 3.14. |
| [flybots](https://pypi.org/project/flybots/) | Nowe; 2.0.0 z 27.08.2026. Ma quadcopter i fixed-wing w jednym pakiecie. | [Modele są w NumPy, a `matplotlib` jest zależnością bazową](https://github.com/guilyx/flybots/blob/main/pyproject.toml); nie daje tensorowego GPU. Projekt ma krótką historię wydań, więc wymaga dodatkowej walidacji. |
| [PyFlyt](https://pypi.org/project/PyFlyt/) | QuadX i fixed-wing; ostatnie wydanie PyPI 0.29.0 z 01.03.2025. | [Wymaga `numpy<2` i PyBullet](https://github.com/jjshoots/PyFlyt/blob/master/pyproject.toml), co koliduje z obecnym `numpy>=2.5.4` i nie zapewnia kroku PyTorch/CUDA. |

Na dziś RotorPy jest najbardziej obiecującą gotową opcją **dla quada**.
Nie znaleziono w powyższym przeglądzie jednego dojrzałego pakietu, który
jednocześnie dostarcza oba typy samolotu, batched PyTorch na CPU/CUDA i pasuje
do obecnych grup zależności. Przed wyborem sprawdzić instalację na macOS CPU
oraz Linux CPU/CUDA, zachowanie resetu wielu środowisk, zgodność układów
współrzędnych i przepustowość kroku bez renderowania.
