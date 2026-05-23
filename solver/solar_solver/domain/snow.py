import numpy as np

class SnowModel:
    @staticmethod
    def calculate_coverage_fraction(snow_depth: float, tilt: float, temp_air: float, ghi: float) -> float:
        """
        Calculates the fraction of the array covered by snow (0.0 to 1.0).
        
        This is a simplified heuristic model:
        - snow_depth: Depth of snow on the ground/panels in cm.
        - tilt: Panel tilt in degrees.
        - temp_air: Ambient temperature in Celsius.
        - ghi: Global Horizontal Irradiance in W/m2.
        """
        if snow_depth <= 0:
            return 0.0
        
        # 1. Gravity (Tilt): Steep panels shed snow much faster.
        # Below ~15 degrees, snow rarely slides off without significant melting.
        tilt_effect = np.clip((tilt - 15.0) / 45.0, 0, 1)
        
        # 2. Thermal (Temp): Snow melts and slides better above freezing.
        temp_effect = np.clip(temp_air / 5.0, 0, 1)
        
        # 3. Solar Heating (GHI): Sun warms the dark cells under the snow.
        ghi_effect = np.clip((ghi - 100.0) / 400.0, 0, 1)
        
        # Heuristic: Total shedding "potential"
        shedding_potential = (tilt_effect * 0.6) + (temp_effect * 0.2) + (ghi_effect * 0.2)
        
        # Multipliers for sticking conditions
        if temp_air <= 0:
            shedding_potential *= 0.5
            
        if ghi < 200:
            shedding_potential *= 0.5
            
        coverage = 1.0 - shedding_potential
        
        return float(np.clip(coverage, 0.0, 1.0))
