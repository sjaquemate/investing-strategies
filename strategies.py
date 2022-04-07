from typing import Callable
import pandas as pd

strategy_fn = Callable[[pd.Series], float]

def lump_sum_gain(data: pd.Series):
    return data[-1] / data[0]

def equal_stock_gain(data: pd.Series):
    return len(data) * data[-1] / sum(data)

def dca_gain(data: pd.Series):
    return sum(1 / data) * data[-1] / len(data)