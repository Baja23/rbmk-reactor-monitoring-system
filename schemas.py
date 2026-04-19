class Reactor:
    def __init__(self, orm_value = 84, partially_inserted = 0, inlet_temp_c = 270.0, outlet_temp_c = 284.0, coolant_flow_m3h = 45000.0, tau = 10.0, thermal_power_mw = 3200.0, reactivity_delta = 0.0, xenon_level = 1.0):
        self.thermal_power_mw = thermal_power_mw
        self.orm_value = orm_value #pręty kontrolne w rdzeniu w 100% wsunięte
        self.partially_inserted = partially_inserted #pręty kontrolne częściowo wsunięte
        self.xenon_level = xenon_level
        self.reactivity_delta = reactivity_delta
        self.inlet_temp_c = inlet_temp_c
        self.outlet_temp_c = outlet_temp_c
        self.coolant_flow_m3h = coolant_flow_m3h
        self.tau = tau

        def thermal_power(self, delta_time):
            power_change = (self.reactivity_delta * self.thermal_power_mw / self.tau) * delta_time
            self.thermal_power_mw += power_change #zmienić
            if self.thermal_power_mw < 160.0: # ~5% mocy to ciepło powyłączeniowe
                self.thermal_power_mw = 160.0

        def positive_void_coefficient(self):
            wynik = 3.068 * (self.thermal_power_mw / self.coolant_flow_m3h) - 0.068
            v_steam = max(0.0, wynik)
            void_reactivity = v_steam * 4.5
            return void_reactivity
        
        #xenon_poisoning
        def xenon_poisoning(self, hist_thermal_power):
            change = ((0.0005 * hist_thermal_power) - (0.0005 * self.xenon_level * self.thermal_power_mw) - (0.00014 * self.xenon_level))
            self.xenon_level = max(0.0, self.xenon_level + change)
            xenon_reactivity = -4.0 * self.xenon_level
            return xenon_reactivity

        #control_rods_insertion
        def control_rods_insertion(self):
            rods_reactivity = -(self.orm_value * 0.06) + (self.partially_inserted * 0.02)
            return rods_reactivity

        def update_reactivity(self, void_reactivity, xenon_reactivity, rods_reactivity):
            self.reactivity_delta = void_reactivity + xenon_reactivity + rods_reactivity