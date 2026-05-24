from dataclasses import dataclass, field

@dataclass
class SandiaInverterParams:
    """Parameters for the Sandia Inverter Model."""
    p_aco: float      # Max AC power (W)
    p_dco: float      # DC power at Paco (W)
    v_dco: float      # DC voltage at Paco (V)
    p_so: float       # Start DC power (W)
    c0: float         # Efficiency coefficient 0
    c1: float         # Efficiency coefficient 1
    c2: float         # Efficiency coefficient 2
    c3: float         # Efficiency coefficient 3
    p_nt: float       # Nighttime tare loss (W)
    v_dc_max: float   # Max DC voltage (V)

class InverterLibrary:
    """A small database of real-world inverter parameters."""
    
    # Example data from Sandia database
    MODELS = {
        "Fronius_Primo_5_0_1": SandiaInverterParams(
            p_aco=5000.0,
            p_dco=5145.0,
            v_dco=370.0,
            p_so=20.0,
            c0=-2.0e-05,
            c1=4.0e-05,
            c2=0.0015,
            c3=0.0003,
            p_nt=0.15,
            v_dc_max=600.0
        ),
        "SMA_Sunny_Boy_5_0": SandiaInverterParams(
            p_aco=5000.0,
            p_dco=5170.0,
            v_dco=365.0,
            p_so=15.0,
            c0=-1.5e-05,
            c1=3.5e-05,
            c2=0.0018,
            c3=0.0002,
            p_nt=0.1,
            v_dc_max=600.0
        )
    }

    @classmethod
    def get(cls, name: str) -> SandiaInverterParams:
        if name not in cls.MODELS:
            raise ValueError(f"Inverter model '{name}' not found in library.")
        return cls.MODELS[name]
