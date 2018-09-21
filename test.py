from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)
client = MongoClient('localhost', 27017)  # localDB

# connect to db
db = client.pattern_poc

# connect to collection
testTable = db.test
dataTable = db.dummyData


# test api
@app.route('/test')
def get_apitest():
    return jsonify({'msg': 'Api is working'})


# test db api
@app.route('/dbtest')
def get_dbtest():
    return dumps(testTable.find({}))


# upload bulk data
@app.route('/uploadCSV', methods=['POST'])
def upload_csv():
    # delete all data
    dataTable.delete_many({})

    # Create variable for uploaded file
    df = pd.read_csv(request.files['fileupload'])

    # conver data to dict
    records_ = df.to_dict(orient='records')

    # upload data to db
    dataTable.insert_many(records_)

    #do something list of dictionaries
    return jsonify({'success': 'Data uploaded successfully!!'})


# get Forex (Uploaded data)
@app.route('/getData')
def get_dummyData():
    _date = []
    _open = []
    _high = []
    _low =[]
    _close = []
    _volume = []
    for data in dataTable.find({}):
        _date.append(data['Time (UTC)'])
        _open.append(data['Open'])
        _high.append(data['High'])
        _low.append(data['Low'])
        _close.append(data['Close'])
        _volume.append(data['Volume '])
    
    return jsonify(
        {'date': _date},
        {'open': _open},
        {'high': _high},
        {'low': _low},
        {'close': _close},
        {'volume': _volume},
    )
    # return dumps(dataTable.find({}))


# @app.route('/')
# def generate_chart():

# run api
if __name__ == '__main__':
    app.run(host='0.0.0.0')
