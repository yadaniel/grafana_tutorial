from bottle import Bottle, HTTPResponse, run, request, response
from bottle import json_dumps
import math
from datetime import datetime
from calendar import timegm

app = Bottle()

@app.get("/")
def index():
    return "OK"

@app.post('/query')
def query():
    if request.json['targets'][0]['type'] == 'table':
        series = request.json['targets'][0]['target']
        bodies = {'series A': [{
        "columns":[
          {"text":"Time","type":"time"},
          {"text":"Country","type":"string"},
          {"text":"Number","type":"number"}
        ],
        "rows":[
          [1234567,"SE",123],
          [1234567,"DE",231],
          [1234567,"US",321]
        ],
        "type":"table"
        }], 'series B': [{
        "columns":[
          {"text":"Time","type":"time"},
          {"text":"Country","type":"string"},
          {"text":"Number","type":"number"}
        ],
        "rows":[
          [1234567,"BE",123],
          [1234567,"GE",231],
          [1234567,"PS",321]
        ],
        "type":"table"
        }]}

        series = request.json['targets'][0]['target']
        body = json_dumps(bodies[series])
        return HTTPResponse(body=body, headers={'Content-Type': 'application/json'})
    else:
        body = []
        start, end = request.json['range']['from'], request.json['range']['to']
        for target in request.json['targets']:
            name = target['target']
            datapoints = create_data_points(FUNCTIONS[name], start, end)
            body.append({'target': name, 'datapoints': datapoints})

        body = json_dumps(body)
    return HTTPResponse(body=body, headers={'Content-Type': 'application/json'})

FUNCTIONS = {'series A': math.sin, 'series B': math.cos}

def convert_to_time_ms(timestamp):
    """Convert a Grafana timestamp to unixtimestamp in milliseconds

        Args:
            timestamp (str): the request contains ``'range': {'from':
                   '2019-06-16T08:00:05.331Z', 'to': '2019-06-16T14:00:05.332Z', ...``
        """
    return 1000 * timegm(datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())

def create_data_points(func, start, end, length=1020):
    """
        A dummy function to produce sine and cosine data

        You should replace this with your SQL, CQL or Mongo Query language.
        Also, make sure your database has the correct indecies to increase perfomance

        Args:
          func (object) - A callable that accepts a number and returns a number
            start (str) - timestamp
            end (str) - timestamp
            length (int) - the number of data points

        """
    lower = convert_to_time_ms(start)
    upper = convert_to_time_ms(end)
    return [[func(i), int(i)] for i in [lower + x*(upper-lower)/length for x in range(length)]]

x = """
@app.post('/query')
def query():
    if request.json['targets'][0]['type'] == 'table':
        series = request.json['targets'][0]['target']
        bodies = {'series A': [{
        "columns":[
          {"text":"Time","type":"time"},
          {"text":"Country","type":"string"},
          {"text":"Number","type":"number"}
        ],
        "rows":[
          [1234567,"SE",123],
          [1234567,"DE",231],
          [1234567,"US",321]
        ],
        "type":"table"
        }], 'series B': [{
        "columns":[
          {"text":"Time","type":"time"},
          {"text":"Country","type":"string"},
          {"text":"Number","type":"number"}
        ],
        "rows":[
          [1234567,"BE",123],
          [1234567,"GE",231],
          [1234567,"PS",321]
        ],
        "type":"table"
        }]}

        series = request.json['targets'][0]['target']
        body = json_dumps(bodies[series])
        return HTTPResponse(body=body, headers={'Content-Type': 'application/json'})
"""

@app.hook('after_request')
def enable_cors():
    print("after_request hook")
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Accept, Content-Type'
    
@app.post('/search')
def search():
    return HTTPResponse(body=json_dumps(['series A', 'series B']), headers={'Content-Type': 'application/json'})

if __name__ == '__main__':
    run(app=app, host='localhost', port=8081)
