class SolarBattery:
    def __init__(self, capacity_kwh, max_charge_kw, max_discharge_kw, efficiency, initial_soc_kwh):
        self.capacity_kwh = capacity_kwh
        self.max_charge_kw = max_charge_kw
        self.max_discharge_kw = max_discharge_kw
        self.efficiency = efficiency
        self.current_soc_kwh = initial_soc_kwh

    def step(self, power_kw, dt_hours=1.0):
        if power_kw > 0:
            charge_power = min(power_kw, self.max_charge_kw)
            energy_to_add = charge_power * dt_hours * self.efficiency
            actual_added = min(energy_to_add, self.capacity_kwh - self.current_soc_kwh)
            self.current_soc_kwh += actual_added
            return charge_power 
        else:
            discharge_req = min(abs(power_kw), self.max_discharge_kw)
            energy_to_take = discharge_req * dt_hours
            actual_taken = min(energy_to_take, self.current_soc_kwh)
            self.current_soc_kwh -= actual_taken
            return -(actual_taken / dt_hours)
