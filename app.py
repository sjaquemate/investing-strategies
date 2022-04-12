import json


def handler(event, context):

    query_string_parameters = event["queryStringParameters"]

    def get_query_parameter(param: str):
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
            'body': json.dumps({'message': str(e)})
        }

    response = {
        'ticker': ticker,
        'start_year': start_year,
        'end_year': end_year,
        'investing_years': investing_years,
    }

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }


def main():
    """ test handler input handling """
    event = {'queryStringParameters': {
        'ticker': "AAPL",
        'start_year': "2000",
        'end_year': "2021",
        'investing_years': "5",
    }}
    
    # todo make these into tests
    print(handler({'queryStringParameters': {}}, {}))
    print(handler(event, {}))
    


if __name__ == "__main__":
    main()
