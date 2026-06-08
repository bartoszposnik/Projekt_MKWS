Projekt realizuje symulację kinetyki chemicznej procesu spalania w reaktorze PSR z wykorzystaniem biblioteki Cantera i mechanizmu GRI-Mech 3.0. Kod pozwala na analizę wpływu wilgotności powietrza dolotowego oraz współczynnika nadmiaru powietrza na temperaturę spalin i emisję tlenków azotu ($\text{NO}_x$), wskazując jednocześnie na ograniczenia numeryczne modeli równowagowych w odwzorowaniu kinetycznego niedopału tlenku węgla ($\text{CO}$).
Warunki wejściowe symulacji (Input Parameters)

Symulację przeprowadzono dla następujących stabilnych parametrów operacyjnych:

-Ciśnienie w komorze (P_wlot): 15 atm

-Temperatura powietrza dolotowego (T_wlot): 650.0 K

-tau_komory: 10 ms

-tau_dopalacza: 20ms

Skład chemiczny paliwa: CH4: 95%, C2H6: 3%, C3H8: 1%, N2: 1%

Zmienne procesowe (Parametric Sweeps)

 phi: 0.5, 0.6, 0.7, 0.8, 0.9, 1.0

Wilgotnosc powietrza dolotowego (Y_H2O): Zakres od 0% do 6% co 0.5%

main.py - kod źródłowy

MKWS.pdf - sprawozdanie
