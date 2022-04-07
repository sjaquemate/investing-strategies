import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass
import yahoo_fin.stock_info as si
from typing import List, Union 
import strategies 

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
        monthly_price = si.get_data(ticker, start_date=datetime(1900, 1, 1), interval="1mo")['open'][:-1]  
        return cls(ticker, monthly_price)
    

def split_into_subintervals(interval: Interval, duration: relativedelta,
                           increment: relativedelta=relativedelta(months=1)) -> List[Interval]:
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


def select_periodic_data(data: pd.DataFrame, interval: Interval, period: relativedelta):
    """ select the closest valid stock dates for periodic dates between an interval """
    dates = []
    date = interval.begin
    while date <= interval.end:
        dates.append(date)
        date += period

    closest_indices = data.index.searchsorted(dates)
    return data.iloc[closest_indices]



def calculate_strategy_gains(data: pd.Series, interval: Interval, strategy_fn: strategies.strategy_fn,
                             buy_period: relativedelta, investing_duration: relativedelta) -> pd.Series:
    """ calculated the fractional realized gains given a certain strategy function in a 
    certain investing_period
    """
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

    def get_timeseries(self) -> pd.Series:
        return self.stock.monthly_price

    def calculate_distribution(self, 
                               strategy_fn: strategies.strategy_fn, 
                               investing_duration: relativedelta, 
                               buy_period: relativedelta,
                               as_percentage=False, yearly=False):
        
        if self.stock is None:
            raise AssertionError("Please set a stock using set_ticker(...)")
        
        if self.interval is None:
            raise AssertionError("Please set an interval using set_interval_years(...)")
         
        gains = calculate_strategy_gains(self.stock.monthly_price, self.interval, strategy_fn,
                                             buy_period=buy_period,
                                             investing_duration=investing_duration)
        if yearly:
            gains = gains ** (1 / investing_duration.years)

        if as_percentage:
            return (gains-1)*100

        return gains