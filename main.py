from dataclasses import dataclass
import pandas as pd
from dateutil.relativedelta import relativedelta
from investing import InvestingModel
import strategies
import json 


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
    # For more information about CORS and CORS preflight requests, see:
    # https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }


    request_json = request.get_json()
    ticker = request_json['ticker']
    start_year = request_json['start_year']
    end_year = request_json['end_year']
    investing_years = request_json['investing_years']

    investingModel = InvestingModel()
    investingModel.set_ticker(ticker)
    investingModel.set_interval_years(start_year, end_year)

    response = {}
    
    timeseries = investingModel.get_timeseries()
    response['timeseries'] = [{'timestamp': timestamp, 'value': value} 
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
        response[strategy_name] = [{'timestamp_start': start, 'timestamp_end': end, 'gain': gain}  
                                       for start, end, gain in zip(start_years, end_years, gains)]

    return (json.dumps(response), 200, headers)


def main():

    from flask import Flask
    with Flask(__name__).app_context():
        
        @dataclass
        class DummyRequest:
            method: int = 0
            
            def get_json():
                return {"ticker": "AAPL",
                        "start_year": 2000,
                        "end_year": 2010,
                        "investing_years": 5}

        response = calculate_investing_distribution(DummyRequest)
        print(response)


if __name__ == "__main__":
    main()
