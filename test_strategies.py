import numpy as np
import strategies
import pytest

range_1to2 = np.linspace(1, 2, 10000)
tolerance = 0.001

def test_lump_sum_gain():
    gain = strategies.lump_sum_gain(range_1to2)
    assert pytest.approx(gain, tolerance) == 2

def test_equal_stock_gain():
    gain = strategies.equal_stock_gain(range_1to2)
    assert pytest.approx(gain, tolerance) == 4/3

def test_dca_gain():
    gain = strategies.dca_gain(range_1to2)
    assert pytest.approx(gain, tolerance) == 2*np.log(2)

