class SolarInverter:
    def __init__(self, pdc0, eta_inv_nom, v_dc_max):
        self.pdc0 = pdc0
        self.eta_inv_nom = eta_inv_nom
        self.v_dc_max = v_dc_max

    def to_pvlib_dict(self):
        return {
            'pdc0': self.pdc0,
            'eta_inv_nom': self.eta_inv_nom,
            'v_dc_max': self.v_dc_max,
        }
