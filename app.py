import json
import investing
import strategies
from datetime import timedelta
import pandas as pd


def to_unix_timestamp(dates):
    return ((pd.Series(dates) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')).tolist()


def handler(event, context):

    def get_query_parameter(param: str):
        if "queryStringParameters" not in event:
            raise AssertionError(f'contains not querystring key')
        query_string_parameters = event["queryStringParameters"]
        if query_string_parameters is None:
            raise AssertionError(
                f'querystring does not contain any parameters')
        if param not in query_string_parameters:
            raise AssertionError(
                f'querystring must contain a {param} parameter')
        return query_string_parameters[param]

    try:
        ticker = get_query_parameter('ticker')
        start_year = int(get_query_parameter('start_year'))
        end_year = int(get_query_parameter('end_year'))
        investing_years = int(get_query_parameter('investing_years'))

    except AssertionError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': str(e)})
        }

    investingModel = investing.InvestingModel()
    investingModel.set_ticker(ticker)
    investingModel.set_interval_years(start_year, end_year)

    timeseries = investingModel.get_timeseries()

    response = {}
    response['timeseries'] = [{'date': date, 'value': value}
        for date, value in zip(to_unix_timestamp(timeseries.index), timeseries.values)]

    response['gains']=[]

    for strategy_name, strategy_fn in strategies.strategies.items():
        gains=investingModel.calculate_distribution(strategy_fn = strategy_fn,
                                                investing_duration = timedelta(
                                                    days=365.25*investing_years),
                                                buy_period = timedelta(days=30.437))

        begin_dates=to_unix_timestamp([begin for begin, _ in gains.index])
        end_dates=to_unix_timestamp([end for _, end in gains.index])
        
        response['gains'].append({
            'strategyName': strategy_name, 
            'data': [{'begin_date': begin_date, 'end_date': end_date, 'value': value}
                     for begin_date, end_date, value in zip(begin_dates, end_dates, gains.values)]
        })

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }
    
if __name__ == "__main__":
    event = {'queryStringParameters': {
        'ticker': "AAPL",
        'start_year': "1900",
        'end_year': "2030",
        'investing_years': "1",
    }}
    print( handler(event, {}) )