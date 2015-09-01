import json, threading
from flask import Flask, render_template, jsonify

from query_client import make_query

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/query')
def query():
    return jsonify(**query_and_format_data())

@app.route('/data')
def data():
    data = {}

    try:
        data_file = open('data.json')
    except: # no data file, we'll just have to wait for the query to finish
        data = query_and_format_data()
    else:
        with data_file:
            data = json.loads(data_file.read())
        # start a query in the background to update data file for next load
        threading.Thread(target=query_and_format_data).start()

    return jsonify(**data)

def query_and_format_data():
    data = make_query('static/js/multi_funnel_query.js')

    with open('data.json', 'w') as f:
        f.write(json.dumps(data))

    return data

if __name__ == '__main__':
    app.run(debug=True)
