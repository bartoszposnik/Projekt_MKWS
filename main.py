import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

print("=== Start symulacji ===")

# =============================================================================
# BLOK 1: INICJALIZACJA BAZY DANYCH I PARAMETRÓW
# =============================================================================
gas = ct.Solution('gri30.yaml')

P_wlot = 15 * ct.one_atm       # Ciśnienie w komorze (15 atm)
T_wlot = 650.0                 # Stabilna temperatura powietrza po sprężarce [K]

tau_komora = 0.010             # Czas przebywania w komorze głównej (10 ms)
tau_dopalania = 0.020          # Czas przebywania w strefie dopalania (20 ms)

# Skład wysokometanowego gazu ziemnego
paliwo_sklad = {'CH4': 0.95, 'C2H6': 0.03, 'C3H8': 0.01, 'N2': 0.01}

# =============================================================================
# BLOK 2: WEKTORY PARAMETRÓW (MACIERZ OBLICZENIOWA)
# =============================================================================
# Oś X: Wilgotność od 0% do 6% (13 punktów)
wilgotnosc_array = np.linspace(0.0, 0.06, 13)

# Badamy wpływ dla różnych współczynników phi (od ubogiej do stechiometrycznej)
phi_array = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

# Główny słownik na przeliczone i znormalizowane wyniki
macierz_wynikow = {}

# =============================================================================
# BLOK 3: DWUWYMIAROWA PĘTLA OBLICZENIOWA 
# =============================================================================
for phi in phi_array:
    print(f"\nObliczenia dla phi = {phi}...")
    
    tymczasowa_T = []
    tymczasowa_NOx = []
    tymczasowa_CO = []
    
    for Y_H2O in wilgotnosc_array:
        # 1. Skład wilgotnego powietrza
        O2_frac = 0.21 * (1.0 - Y_H2O)
        N2_frac = 0.79 * (1.0 - Y_H2O)
        powietrze_sklad = {'O2': O2_frac, 'N2': N2_frac, 'H2O': Y_H2O}
        
        # 2. Inicjalizacja chemiczna przez equilibrate (HP) - wymuszenie zapłonu
        gas.set_equivalence_ratio(phi=phi, fuel=paliwo_sklad, oxidizer=powietrze_sklad)
        gas.TP = T_wlot, P_wlot
        gas.equilibrate('HP') 
        
        # 3. Krok I: Główna komora jako stabilny reaktor zamknięty w czasie
        r = ct.IdealGasConstPressureReactor(gas, clone=True)
        sim = ct.ReactorNet([r])
        sim.advance(tau_komora) 
        
        # 4. Krok II: Strefa Dopalania (PFR) - kolejne 20 ms
        gas.TPY = r.phase.T, P_wlot, r.phase.Y
        pfr = ct.IdealGasConstPressureReactor(gas, clone=True)
        sim_pfr = ct.ReactorNet([pfr])
        sim_pfr.advance(tau_dopalania)
        
        stan_koncowy = pfr.phase
        
        # 5. Ekstrakcja danych i normalizacja do mg/Nm3 @ 15% O2
        T_koncowa = stan_koncowy.T
        
        # Bezpieczne pobranie słownika (zapobiega błędom ValueError)
        ulamki_molowe = stan_koncowy.mole_fraction_dict()
        
        X_O2 = ulamki_molowe.get('O2', 0.0)
        X_NO = ulamki_molowe.get('NO', 0.0)
        X_NO2 = ulamki_molowe.get('NO2', 0.0)
        X_CO = ulamki_molowe.get('CO', 0.0)
        
        O2_procent = X_O2 * 100
        
        # Zabezpieczenie matematyczne dla korekcji tlenowej
        if O2_procent < 20.9:
            korekcja_O2 = (21.0 - 15.0) / (21.0 - O2_procent)
        else:
            korekcja_O2 = 1.0
            
        NOx_ppm = (X_NO + X_NO2) * 1e6
        CO_ppm = X_CO * 1e6
        
        # Przeliczenie ppm -> mg/Nm3 z zachowaniem identycznego nazewnictwa zmiennych
        NOx_mgNm3 = NOx_ppm * korekcja_O2 * (46.0 / 22.4)
        CO_mgNm3 = CO_ppm * korekcja_O2 * (28.0 / 22.4)
        
        # Dopisanie do list tymczasowych dla bieżącego phi
        tymczasowa_T.append(T_koncowa)
        tymczasowa_NOx.append(NOx_mgNm3)
        tymczasowa_CO.append(CO_mgNm3)
        
    # Zapis serii danych do macierzy głównej
    macierz_wynikow[phi] = {
        'T': np.array(tymczasowa_T),
        'NOx': np.array(tymczasowa_NOx),
        'CO': np.array(tymczasowa_CO)
    }

# =============================================================================
# BLOK 4: GENEROWANIE ZAAWANSOWANYCH WYKRESÓW ROZSTRZYGAJĄCYCH
# =============================================================================
print("\nGenerowanie ostatecznych wykresów...")
wilgotnosc_procenty = wilgotnosc_array * 100

plt.figure(figsize=(11, 11))

# Wykres 1: Temperatura spalin
plt.subplot(3, 1, 1)
for phi in phi_array:
    plt.plot(wilgotnosc_procenty, macierz_wynikow[phi]['T'], '-o', label=f'$\\phi$ = {phi}', linewidth=1.8)
plt.title('Wpływ wilgotności i $\\phi$ w zaawansowanym modelu hybrydowym (PSR + PFR)', fontsize=12, fontweight='bold')
plt.ylabel('Temperatura spalin [K]')
plt.grid(True, linestyle='--')
plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left')

# Wykres 2: Ekologiczna emisja NOx
plt.subplot(3, 1, 2)
for phi in phi_array:
    plt.plot(wilgotnosc_procenty, macierz_wynikow[phi]['NOx'], '-s', label=f'$\\phi$ = {phi}', linewidth=1.8)
plt.ylabel('Emisja NOx [mg/Nm³ @ 15% O2]')
plt.grid(True, linestyle='--')

# Wykres 3: Ekologiczna emisja CO
plt.subplot(3, 1, 3)
for phi in phi_array:
    plt.plot(wilgotnosc_procenty, macierz_wynikow[phi]['CO'], '-^', label=f'$\\phi$ = {phi}', linewidth=1.8)
plt.xlabel('Wilgotność powietrza dolotowego [%]')
plt.ylabel('Emisja CO [mg/Nm³ @ 15% O2]')
plt.grid(True, linestyle='--')

plt.tight_layout()
plt.savefig('wyniki_ostateczne_2D.png', dpi=300, bbox_inches='tight')
print("Sukces. Wykres zapisano jako 'wyniki_ostateczne_2D.png'.")
plt.show()