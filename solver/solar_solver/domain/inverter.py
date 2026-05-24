from .inverter_library import SandiaInverterParams
from pvlib.inverter import sandia

class SolarInverter:
    def __init__(self, pdc0: float, eta_inv_nom: float, v_dc_max: float, sandia_params: SandiaInverterParams = None):
        self.pdc0 = pdc0
        self.eta_inv_nom = eta_inv_nom
        self.v_dc_max = v_dc_max
        self.sandia_params = sandia_params

    def to_pvlib_dict(self):
        d = {
            'pdc0': self.pdc0,
            'eta_inv_nom': self.eta_inv_nom,
            'v_dc_max': self.v_dc_max,
        }
        if self.sandia_params:
            d.update({
                'Paco': self.sandia_params.p_aco,
                'Pdco': self.sandia_params.p_dco,
                'Vdco': self.sandia_params.v_dco,
                'Pso': self.sandia_params.p_so,
                'C0': self.sandia_params.c0,
                'C1': self.sandia_params.c1,
                'C2': self.sandia_params.c2,
                'C3': self.sandia_params.c3,
                'Pnt': self.sandia_params.p_nt,
            })
        return d

    def calculate_ac(self, dc_power: float, dc_voltage: float = None) -> float:
        """
        Calculates AC power output (W) from DC power (W).
        """
        if not self.sandia_params:
            return dc_power * self.eta_inv_nom
        
        v_dc = dc_voltage if dc_voltage is not None else self.sandia_params.v_dco
        
        return sandia(v_dc, dc_power, self.to_pvlib_dict())
