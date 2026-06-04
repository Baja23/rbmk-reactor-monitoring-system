import time


class Reactor:
    def __init__(self, **conv_data):
        for k, v in conv_data.items():
            setattr(self, k, v)
        self.rod_counter = 1
        self.rod_change_list = []


        # self.thermal_power_mw = conv_data.values("thermal_power_mw")
        # self.orm_value = orm_value  # pręty kontrolne w rdzeniu w 100% wsunięte
        # self.partially_inserted = partially_inserted  # pręty kontrolne częściowo wsunięte
        # self.xenon_level = xenon_level
        # self.reactivity_delta = reactivity_delta
        # self.inlet_temp_c = inlet_temp_c
        # self.outlet_temp_c = outlet_temp_c
        # self.coolant_flow_m3h = coolant_flow_m3h
        # self.tau = tau
        # self.fuel_reactivity = fuel_reactivity
        # self.neutron_flux_pct = neutron_flux_pct
        # self.severity_level = severity_level
        # self.subsystem = subsystem
        # self.alarm_message = alarm_message


    def thermal_power(self, delta_time):
        self.rod_change = (self.reactivity_delta * self.thermal_power_mw / self.tau) * delta_time
        self.thermal_power_mw += self.rod_change  # zmienić
        if self.thermal_power_mw < 160.0:  # ~5% mocy to ciepło powyłączeniowe
            self.thermal_power_mw = 160.0

    def positive_void_coefficient(self):
        subcooling_margin = self.outlet_temp_c - self.inlet_temp_c 
        raw_voids = (3.068 * (self.thermal_power_mw / self.coolant_flow_m3h)) - (subcooling_margin * 0.005)
        
        v_steam = max(0.0, raw_voids)
        
        void_reactivity = v_steam * 4.5
        return void_reactivity

    # xenon_poisoning
    def xenon_poisoning(self, hist_thermal_power=3200, delta_t=1.0):
        production = 0.00005 * hist_thermal_power
        
        burnup = 0.00005 * self.xenon_level * self.thermal_power_mw
        
        decay = 0.00021 * self.xenon_level
        
        change = (production - burnup - decay) * delta_t
        self.xenon_level = max(0.0, self.xenon_level + change)
        
        xenon_reactivity = -4.0 * self.xenon_level
        return xenon_reactivity

    # control_rods_insertion
    def control_rods_insertion(self):
        rods_reactivity = -(self.orm_value * 0.06) + (self.partially_inserted * 0.02)
        print(f"Rods reactivity: {rods_reactivity}")
        return rods_reactivity

    def update_reactor_state(self, hist_thermal_power, delta_t=1.0):
        # KROK 1: Wyliczenie wszystkich oporów i przyspieszeń
        void_rho = self.positive_void_coefficient()
        xenon_rho = self.xenon_poisoning(hist_thermal_power, delta_t)
        rods_rho = self.control_rods_insertion()
        
        # KROK 2: Bilans Reaktywności (Całkowita Suma)
        # fuel_reactivity to nasza idealna podstawa wyliczona przy kalibracji na start
        self.reactivity_delta = self.fuel_reactivity + void_rho + xenon_rho + rods_rho
        
        # KROK 3: Wykładnicza zmiana mocy cieplnej
        # Zależy od całkowitej reaktywności i stałej czasowej (tau)
        power_change = (self.reactivity_delta * self.thermal_power_mw / self.tau) * delta_t
        self.thermal_power_mw += power_change
        
        # Zabezpieczenie fizyczne: Ciepło powyłączeniowe (Decay Heat)
        # Z rozpadu promieniotwórczego, zawsze emitowane jest ok. 5% ciepła, nawet po wciśnięciu AZ-5
        if self.thermal_power_mw < 160.0:
            self.thermal_power_mw = 160.0
            
        # KROK 4: Skorelowanie Strumienia Neutronów
        # Strumień (w %) to po prostu relacja obecnej mocy cieplnej z rozszczepień do mocy nominalnej (3200)
        self.neutron_flux_pct = (self.thermal_power_mw / 3200.0) * 100.0



    def automatic_regulator(self, delta_t=1.0):
            """
            Symuluje system LAR/AR (Lokalny Automatyczny Regulator).
            Koryguje moc poprzez powolne opuszczanie/podnoszenie prętów w strefie boru.
            """
            target_power = 3200.0
            
            # 1. Obliczenie uchybu
            error = self.thermal_power_mw - target_power
            
            # 2. STREFA NIECZUŁOŚCI (Deadband)
            # AR nie reaguje, jeśli moc waha się minimalnie (np. +/- 15 MW). 
            # Zapobiega to "drżeniu" prętów w każdej sekundzie.
            if abs(error) < 15.0:
                return # Reaktor jest stabilny, nie robimy nic
                
            # 3. KIERUNEK RUCHU
            # Używamy float zamiast int, aby symulować np. ruch pręta o pół metra w ciągu sekundy.
            # Wartość 0.005 to tzw. "Wzmocnienie Regulatora" - im mniejsza, tym spokojniejszy ruch.
            rod_movement = error * 0.05 * delta_t 
            
            # 4. LIMIT PRĘDKOŚCI RUCHU
            # AR nie może poruszyć nagle 40 prętów. Może zmienić odpowiednik np. max 10 prętów na sekundę.
            # Funkcja min() i max() docina wartość do bezpiecznego przedziału [-10.0, 10.0]
            rod_movement = max(-10.0, min(rod_movement, 10.0))
            
            # 5. AKTUALIZACJA STANU RDZENIA
            # Jeśli moc jest za duża (error > 0), rod_movement jest dodatni. 
            # Dodajemy tę wartość do orm_value (więcej boru w rdzeniu -> moc spadnie).
            # Jeśli moc jest za mała (error < 0), rod_movement jest ujemny (wyciągamy bor -> moc wzrośnie).
            new_orm = self.orm_value + rod_movement
            
            # 6. ZABEZPIECZENIA FIZYCZNE
            # Nie możemy mieć mniej niż 0 prętów (całkowicie wyciągnięte) 
            # i nie więcej niż zadeklarowana liczba dostępnych w strefie.
            max_available_rods = 211 - self.partially_inserted
            self.orm_value = max(0.0, min(new_orm, max_available_rods))

def reactor_run(reactor: object, delta_time: float):
    void_reactivity = reactor.positive_void_coefficient()
    xenon_reactivity = reactor.xenon_poisoning()
    rods_reactivity = reactor.control_rods_insertion()
    reactor.update_reactor_state(reactor.thermal_power_mw, delta_time)
    reactor.automatic_regulator(delta_time)
    time.sleep(delta_time)
