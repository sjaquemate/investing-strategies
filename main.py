from flask import make_response
import pandas as pd
from dateutil.relativedelta import relativedelta
from investing import InvestingModel
import strategies

def to_timestamp(dates):
    return (dates - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    
def calculate_investing_distribution(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    ticker = request_json['ticker']
    start_year = request_json['start_year']
    end_year = request_json['end_year']
    investing_years = request_json['investing_years']

    investingModel = InvestingModel()
    investingModel.set_ticker(ticker)
    investingModel.set_interval_years(start_year, end_year)

    response_dct = {}
    
    timeseries = investingModel.get_timeseries()
    response_dct['timeseries'] = [{'timestamp': timestamp, 'value': value} 
                                 for timestamp, value in zip(to_timestamp(timeseries.index), timeseries)]
    
    for strategy_name, strategy_fn in {
        'lump_sum': strategies.lump_sum_gain,
        'equal_stock': strategies.equal_stock_gain,
        'dca': strategies.dca_gain,
    }.items():

        gains = investingModel.calculate_distribution(strategy_fn=strategy_fn,
                                                      investing_duration=relativedelta(
                                                          years=investing_years),
                                                      buy_period=relativedelta(months=1))
        
        start_years = pd.Series([start for start, end in gains.index.values])
        end_years = pd.Series([end for start, end in gains.index.values])

        start_years = to_timestamp(start_years)
        end_years = to_timestamp(end_years)
        response_dct[strategy_name] = [{'timestamp_start': start, 'timestamp_end': end, 'gain': gain}  
                                       for start, end, gain in zip(start_years, end_years, gains)]

    return make_response(response_dct)


def main():

    from flask import Flask
    with Flask(__name__).app_context():
        class DummyRequest:
            def get_json():
                return {"ticker": 'AAPL',
                        "start_year": 2000,
                        "end_year": 2010,
                        "investing_years": 5}

        response = calculate_investing_distribution(DummyRequest)
        print(response.get_json())


if __name__ == "__main__":
    main()
