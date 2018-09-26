from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

app = Flask(__name__)
CORS(app)
client = MongoClient('localhost', 27017)  # localDB

# connect to db
db = client.pattern_poc

# connect to collection
testTable = db.test
dataTable = db.dummyData
finalPatterns = []


def remove_duplication(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


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

    # convert data to dict
    records_ = df.to_dict(orient='records')

    # upload data to db
    dataTable.insert_many(records_)

    return jsonify({'success': 'Data uploaded successfully!!'})


# get Forex (Uploaded data)
@app.route('/getData')
def get_dummyData():
    _date = []
    _open = []
    _high = []
    _low = []
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
        {
            'date': _date
        },
        {'open': _open},
        {'high': _high},
        {'low': _low},
        {'close': _close},
        {'volume': _volume},
    )
    # return dumps(dataTable.find({}))

# for triangle pattern optimised
def best_pattern(pattern):
    if pattern:
        # print(pattern)
        temp = []
        for last in pattern:
            temp.append(last[2][1])
        finalPatterns.append(pattern[temp.index(min(temp))])
        print(finalPatterns, '***************')

@app.route('/getTrianglePattern')
def triangle_pattern():
    volume = []
    date = []
    trianglePattern = []
    firstpoint = []
    peakoint = []
    lastpoint = []

    for data in dataTable.find({}):
        volume.append(data['Volume '])
        date.append(data['Time (UTC)'])

    data = pd.DataFrame({'vol': volume})
    data = data.drop_duplicates(keep=False)

    data.columns = [['vol']]

    _volume = data['vol']

    # print(_volume)

    for i in range(0, len(_volume)):
        max_idx = list(
            argrelextrema(_volume.values[:i], np.greater, order=10)[0])
        min_idx = list(argrelextrema(_volume.values[:i], np.less, order=10)[0])

        idx = max_idx + min_idx + [len(_volume[:i] - 1)]

        idx.sort()

        current_idx = idx[-3:]

        start = min(current_idx)
        end = max(current_idx)

        current_pat = _volume.values[current_idx]

        peaks = _volume.values[idx]

        if (len(current_idx) == 3):
            XA = current_pat[1] - current_pat[0]
            AB = current_pat[2] - current_pat[1]

            if XA > 0 and AB < 0:
                # trianglePattern.append(current_pat)
                trianglePattern.append([
                    [
                        date[volume.index(current_pat[0])],
                        volume[volume.index(current_pat[0])]
                    ],
                    [
                        date[volume.index(current_pat[1])],
                        volume[volume.index(current_pat[1])]
                    ],
                    [
                        date[volume.index(current_pat[2])],
                        volume[volume.index(current_pat[2])]
                    ],
                ])
                firstpoint.append(volume[volume.index(current_pat[0])])
                peakoint.append(volume[volume.index(current_pat[1])])
                lastpoint.append(volume[volume.index(current_pat[2])])

    # peakoint = remove_duplication(peakoint)
    # firstpoint = remove_duplication(firstpoint)
    # lastpoint = remove_duplication(lastpoint)
    firstPattern = []
    first = trianglePattern[0][0][1]
    for i in range(0, len(trianglePattern)):
        if first != trianglePattern[i][0][1]:
            if firstPattern:
                # print(pattern)
                temp = []
                for last in firstPattern:
                    temp.append(last[2][1])
                finalPatterns.append(firstPattern[temp.index(min(temp))])
                # print(finalPatterns, '***************')
            firstPattern = []
            first = trianglePattern[i][0][1]
            # break
        else:
            # print(i, trianglePattern[i])
            firstPattern.append(trianglePattern[i])

    print("PeakPoints : ", len(peakoint), " : ")
    print("FirstPoints : ", len(firstpoint), " : ")
    print("LastPoints : ", len(lastpoint), " : ")

    return (jsonify({"trianglePattern": finalPatterns}))

# run api
if __name__ == '__main__':
    app.run(host='0.0.0.0')
