from flask import make_response

from investing import InvestingModel


def hello_world(request):
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
    # start_year = request_json['start_year']
    # end_year = request_json['end_year']
    
    investingModel = InvestingModel()
    investingModel.set_ticker(ticker)
    return make_response( {'timeseries': investingModel.get_timeseries().tolist()} )    
