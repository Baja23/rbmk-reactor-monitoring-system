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
        wynik = 3.068 * (self.thermal_power_mw / self.coolant_flow_m3h) - 0.068
        v_steam = max(0.0, wynik)
        void_reactivity = v_steam * 4.5
        print(f"Void reactivity: {void_reactivity}")
        return void_reactivity

    # xenon_poisoning
    def xenon_poisoning(self, hist_thermal_power=3200.0):
        self.rod_change = ((0.00005 * hist_thermal_power) - (0.00005 * self.xenon_level * self.thermal_power_mw) - (self.xenon_level - (0.0021 * self.xenon_level)))
        self.xenon_level = max(0.0, self.xenon_level + self.rod_change)
        xenon_reactivity = -4.0 * self.xenon_level
        print(f"Xenon level: {self.xenon_level}")
        print(f"Xenon reactivity: {xenon_reactivity}")
        return xenon_reactivity

    # control_rods_insertion
    def control_rods_insertion(self):
        rods_reactivity = -(self.orm_value * 0.06) + (self.partially_inserted * 0.02)
        print(f"Rods reactivity: {rods_reactivity}")
        return rods_reactivity

    def update_reactivity(self, void_reactivity, xenon_reactivity, rods_reactivity):
        self.reactivity_delta = self.fuel_reactivity + void_reactivity + xenon_reactivity + rods_reactivity



    def rods_change(self, thermal_power):
        """Insert and eject rods from reactor"""

        print(f"Counter count: {self.rod_counter}")
        target_power = 3200

        print(thermal_power)
        error  = int(thermal_power) - target_power # Checks the delta between desired output and current output
        # error = error * (abs(error) >= 50)
        print(f"Error value: {error}")
        available_rods = 211 - self.orm_value - self.partially_inserted # Gives a number of available rods
        print(f"Available rods: {available_rods}")
        self.rod_change = int(error * 0.06) # Calculates how many rods should be inserted/ejected based on error value
        print(f"Rod change: {self.rod_change}")
        self.rod_change = min(max(-40, min(self.rod_change, 40)), available_rods) # Limits the rod movement to -40 or 40, or if rods insertion exceeds available rods, it's set to the value of available rods

        if self.rod_change < 0: # This conditional is to check if rod movement would leave inserted rods below 0 value
            if self.orm_value + self.rod_change < 0:
                self.rod_change = self.rod_change + (abs(self.rod_change + self.orm_value))
                print(f"Orm_value after abs: {self.orm_value}")

        # if error > 300 or error < -300:
        #     self.rod_change = int(self.rod_change * 1.2)

        self.rod_change_list.append(self.rod_change)
        print(f"Rod change list: {self.rod_change_list[0]}")

        if self.rod_change_list[0] == 0: # The actual purpose of the list is to store the original single variable.
                                         # Simulation goes in the loop, so it's impossible to store a value in a variable
                                         # To circumvene that a list is created where only first element will be used
            del self.rod_change_list[0]  # We delete the first element if it is equal to 0 to let the conditionals below work

        # Rods control need to finish its work before



        try:
            if self.rod_change_list[0] > 0 and available_rods > 0: # available_rods to change
                if self.rod_counter == 1:
                    self.partially_inserted += self.rod_change_list[0]
                if self.rod_counter == 2:
                    self.partially_inserted -= self.rod_change_list[0]
                    self.orm_value += self.rod_change_list[0]
                    del self.rod_change_list[:]
                    self.rod_counter = 0
                self.rod_counter += 1


            elif self.rod_change_list[0] < 0 and self.partially_inserted >= 0: # partially_inserted to change
                print("Test elif")
                if self.rod_counter == 1:
                    self.orm_value += self.rod_change_list[0]
                    self.partially_inserted -= self.rod_change_list[0]
                if self.rod_counter == 2:
                    self.partially_inserted += self.rod_change_list[0]
                    del self.rod_change_list[:]
                    self.rod_counter =0
                self.rod_counter += 1

        except IndexError:
            pass

            if available_rods == 0:
                print("No rods available.")
            elif self.partially_inserted < 0:
                print("Partially inserted rods can't go below 0.")

        print(f"Orm, par values: {self.orm_value}, {self.partially_inserted}")






def reactor_run(reactor: object, delta_time: float):
    void_reactivity = reactor.positive_void_coefficient()
    xenon_reactivity = reactor.xenon_poisoning()
    rods_reactivity = reactor.control_rods_insertion()
    reactor.update_reactivity(void_reactivity, xenon_reactivity, rods_reactivity)
    reactor.thermal_power(delta_time)
    time.sleep(delta_time)
