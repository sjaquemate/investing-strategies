from app import handler 


def expect_statusCode(response, code):
    assert response['statusCode'] == code
    
def test_handler():
    """ test handler input handling """
    event = {'queryStringParameters': {
        'ticker': "AAPL",
        'start_year': "2000",
        'end_year': "2021",
        'investing_years': "5",
    }}
    
    expect_statusCode( handler({'queryStringParameters': None}, {}), 400 )
    expect_statusCode( handler({'queryStringParameters': {}}, {}), 400 )
    expect_statusCode( handler(event, {}), 200 )