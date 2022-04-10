import pandas as pd
from dateutil.relativedelta import relativedelta
from investing import InvestingModel
import strategies
import json


def to_timestamp(dates):
    return (dates - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')


def calculate_all_gains(ticker: str, 
                        start_year: int , 
                        end_year: int, 
                        investing_years: int) -> dict: 

    investingModel = InvestingModel()
    investingModel.set_ticker(ticker)
    investingModel.set_interval_years(start_year, end_year)

    response = {}

    timeseries = investingModel.get_timeseries()
    response['timeseries'] = [{'timestamp': timestamp, 'value': value}
                              for timestamp, value in zip(to_timestamp(timeseries.index), timeseries)]

    strategy_options = {
        'lump_sum': strategies.lump_sum_gain,
        'equal_stock': strategies.equal_stock_gain,
        'dca': strategies.dca_gain,
    }
    
    for strategy_name, strategy_fn in strategy_options.items():

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

    return response


def lambda_handler(event, context):
    # https://www.youtube.com/watch?v=UQiRhKgQ5X0
    # https://github.com/alfonsof/aws-python-examples/blob/master/awslambdahttprequest/lambda_function.py
    body = {}
    if 'queryStringParameters' in event:
        
        ticker =  event['queryStringParameters']['ticker']
        start_year = event['queryStringParameters']['start_year']
        end_year = event['queryStringParameters']['end_year']
        investing_years = event['queryStringParameters']['investing_years']

        body = calculate_all_gains(ticker, start_year, end_year, investing_years)
        
    return {
        'statusCode': 200,
        'body': json.dumps(body),
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }


def main():
    response = lambda_handler({'queryStringParameters': {
        'ticker': 'AAPL',
        'start_year': 2000,
        'end_year': 2010,
        'investing_years': 5,
        }}, {})
    print(response)
    
if __name__ == "__main__":
    main()