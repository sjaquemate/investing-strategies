import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
import yahoo_fin.stock_info as si
from typing import List, Union 
import strategies 
import numpy as np 

@dataclass
class Interval:
    begin: datetime
    end: datetime
    
@dataclass
class Stock:
    ticker: str
    monthly_price: pd.DataFrame()

    @classmethod
    def from_ticker(cls, ticker):
        # set monthly price excluding the last month
        data = si.get_data(ticker, start_date=datetime(1900, 1, 1), interval="1mo")
        monthly_price = data['open'][:-1]  
        return cls(ticker, monthly_price)
    

def split_into_subintervals(interval: Interval, duration: timedelta,
                           increment: timedelta=timedelta(days=30.437)) -> List[Interval]:
    """ split and interval into subintervals of certain durations,
    e.g: interval: (2000, 2005), duration: 1 year, increment: 1 month ->
         [(jan 2000, jan 2001), (feb 2000, feb 2001), ..., (dec 2003, dec 2004)]
    """
    subintervals = []
    subinterval = Interval(interval.begin, interval.begin + duration)
    while subinterval.end < interval.end:
        subintervals.append(subinterval)
        subinterval = Interval(subinterval.begin + increment,
                               subinterval.end + increment)
    return subintervals


def select_periodic_data(data: pd.DataFrame, interval: Interval, period: timedelta):
    """ select the closest valid stock dates for periodic dates between an interval """
    dates = np.arange(interval.begin, interval.end, period)
    closest_indices = data.index.searchsorted(dates)
    return data.iloc[closest_indices]



def calculate_strategy_gains(data: pd.Series, interval: Interval, strategy_fn: strategies.strategy_fn,
                             buy_period: timedelta, investing_duration: timedelta) -> pd.Series:
    """ calculated the fractional realized gains given a certain strategy function in a 
    certain investing_period
    """
    interval = Interval( max(interval.begin, data.index.min()),
                         min(interval.end, data.index.max()))  # don't calculate more than is available
    subintervals = split_into_subintervals(interval, investing_duration)

    gains = []
    for subinterval in subintervals:
        prices = select_periodic_data(data, subinterval, buy_period)
        gain = strategy_fn(prices)
        gains.append(gain)

    gains_series = pd.Series(gains, 
                             index=[(subinterval.begin, subinterval.end) for subinterval in subintervals])
    return gains_series


@dataclass 
class InvestingModel:

    stock: Union[Stock, None] = None
    interval: Union[Interval, None] = None

    def set_interval_years(self, begin: int, end: int):
        self.interval = Interval(datetime(begin, 1, 1), datetime(end, 1, 1))

    def set_ticker(self, ticker):
        if self.stock is not None and ticker == self.stock.ticker:
            return

        self.stock = Stock.from_ticker(ticker)

    def get_stockname(self) -> str:
        return ''
    
    def get_timeseries(self) -> pd.Series:
        return self.stock.monthly_price

    def calculate_distribution(self, 
                               strategy_fn: strategies.strategy_fn, 
                               investing_duration: timedelta, 
                               buy_period: timedelta):
        
        if self.stock is None:
            raise AssertionError("Please set a stock using set_ticker(...)")
        
        if self.interval is None:
            raise AssertionError("Please set an interval using set_interval_years(...)")
         
        gains = calculate_strategy_gains(self.stock.monthly_price, self.interval, strategy_fn,
                                             buy_period=buy_period,
                                             investing_duration=investing_duration)

        return gains