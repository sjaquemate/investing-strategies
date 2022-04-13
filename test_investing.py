from datetime import datetime
from dateutil.relativedelta import relativedelta
import investing
import strategies

investingModel = investing.InvestingModel()

def test_timeseries():
    investingModel.set_ticker('AAPL')  # Apple
    timeseries = investingModel.get_timeseries()
    assert timeseries.index.min() < datetime(1990, 1, 1)
    assert timeseries.index.max() > datetime.now() - relativedelta(days=40)


def test_gains():
    investingModel.set_ticker('^GSPC')  # S&P500
    investingModel.set_interval_years(2000, 2010)
    gains = investingModel.calculate_distribution(strategy_fn=strategies.lump_sum_gain,
                                                  investing_duration=relativedelta(years=5),
                                                  buy_period=relativedelta(months=2))
    assert len(gains) == (10 - 5)*12