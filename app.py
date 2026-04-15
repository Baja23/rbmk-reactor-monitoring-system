class Reactor:
    def __init__(self, neutron_flux_pct, orm_value, insertion_pct, xenon_level, inlet_temp_c, outlet_temp_c, coolant_flow_m3h, tau = 10.0, thermal_power_mw = 3200.0, reactivity_delta = 0.0):
        self.thermal_power_mw = thermal_power_mw
        self.neutron_flux_pct = neutron_flux_pct
        self.orm_value = orm_value
        self.insertion_pct = insertion_pct
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
            return v_steam
        
        #xenon_poisoning  neutron flux
        #control_rods_insertion

        def update_reactivity(self, void_reactivity, xenon_reactivity, rods_reactivity):
            self.reactivity_delta = void_reactivity + xenon_reactivity + rods_reactivity