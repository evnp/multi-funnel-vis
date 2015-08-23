from flask import Flask, render_template, jsonify
app = Flask(__name__)

from query_client import make_query

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/query')
def query():
    result = make_query('static/js/multi_funnel_query.js')
    print result
    return jsonify(**result)

if __name__ == '__main__':
    app.run(debug=True)
