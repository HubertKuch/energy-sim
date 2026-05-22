class SolarPanel:
    def __init__(self, pdc0, v_mp, i_mp, v_oc, i_sc, gamma_pdc, alpha_sc, beta_voc, cells_in_series):
        self.pdc0 = pdc0
        self.v_mp = v_mp
        self.i_mp = i_mp
        self.v_oc = v_oc
        self.i_sc = i_sc
        self.gamma_pdc = gamma_pdc
        self.alpha_sc = alpha_sc
        self.beta_voc = beta_voc
        self.cells_in_series = cells_in_series

    def to_pvlib_dict(self):
        return {
            'pdc0': self.pdc0,
            'v_mp': self.v_mp,
            'i_mp': self.i_mp,
            'v_oc': self.v_oc,
            'i_sc': self.i_sc,
            'gamma_pdc': self.gamma_pdc,
            'alpha_sc': self.alpha_sc,
            'beta_voc': self.beta_voc,
            'cells_in_series': self.cells_in_series,
        }
