import pytest
from solar_solver.domain.snow import SnowModel

def test_snow_coverage_no_snow():
    assert SnowModel.calculate_coverage_fraction(0, 30, 0, 500) == 0.0
    assert SnowModel.calculate_coverage_fraction(-1, 30, 0, 500) == 0.0

def test_snow_coverage_full_cold_flat():
    # 10cm snow, 0 tilt, -10C, low sun -> Should be 100% covered
    coverage = SnowModel.calculate_coverage_fraction(10, 0, -10, 100)
    assert coverage == 1.0

def test_snow_shedding_tilt():
    # Comparing 15 deg vs 45 deg tilt at 0C and 200 GHI
    cov_low = SnowModel.calculate_coverage_fraction(5, 15, 0, 200)
    cov_high = SnowModel.calculate_coverage_fraction(5, 45, 0, 200)
    assert cov_high < cov_low

def test_snow_shedding_temperature():
    # Comparing -5C vs +5C at 30 deg tilt and 200 GHI
    cov_cold = SnowModel.calculate_coverage_fraction(5, 30, -5, 200)
    cov_warm = SnowModel.calculate_coverage_fraction(5, 30, 5, 200)
    assert cov_warm < cov_cold

def test_snow_shedding_ghi():
    # Comparing 100 vs 800 GHI at 30 deg tilt and 0C
    cov_low_sun = SnowModel.calculate_coverage_fraction(5, 30, 0, 100)
    cov_high_sun = SnowModel.calculate_coverage_fraction(5, 30, 0, 800)
    assert cov_high_sun < cov_low_sun
