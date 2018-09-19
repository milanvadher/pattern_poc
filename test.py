from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
import pandas as pd

app = Flask(__name__)
client = MongoClient('localhost', 27017)  # localDB

# connect to db
db = client.pattern_poc

# connect to collection
testTable = db.test
dataTable = db.dummyData

@app.route('/test')
def get_apitest():
    return jsonify({'msg': 'Api is working'})

@app.route('/dbtest')
def get_dbtest():
    return dumps(testTable.find({}))

@app.route('/uploadCSV', methods=['POST'])
def upload_csv():

    # Create variable for uploaded file
    df = pd.read_csv(request.files['fileupload'])
    
    records_ = df.to_dict(orient = 'records')
    dataTable.insert_many(records_ )

    #do something list of dictionaries
    return jsonify({'success': 'File uploaded successfully!!'})


@app.route('/getData')
def get_dummyData():
    return dumps(dataTable.find({}))

if __name__ == '__main__':
    app.run()