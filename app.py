import json
import investing 
import strategies 
from dateutil.relativedelta import relativedelta


def handler(event, context):


    def get_query_parameter(param: str):
        if "queryStringParameters" not in event:
            raise AssertionError(f'contains not querystring key')
        query_string_parameters = event["queryStringParameters"]
        if query_string_parameters is None:
            raise AssertionError(f'querystring does not contain any parameters')
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
    gains = investingModel.calculate_distribution(strategy_fn=strategies.lump_sum_gain,
                                                  investing_duration=relativedelta(years=investing_years),
                                                  buy_period=relativedelta(months=1))
    
    response = {}
    response['timeseries'] = {
        'dates': timeseries.index.astype(str).tolist(),
        'values': timeseries.values.tolist(),
    }
    dates = [str(start) + ' ' + str(end) for start, end in gains.index]
    response['gains'] = {
        'dates': dates,
        'values': gains.values.tolist(),
    }
    # response['event'] = event

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
        'start_year': "2000",
        'end_year': "2010",
        'investing_years': "5",
    }}
    print( handler(event, {}) )