# -*- encoding:utf-8 -*-
from flask import json
from flask import Flask
from flask import render_template
from flask import request
import sys

sys.path.append("..")

from ZHtrend.DB import db

app = Flask(__name__)


@app.route('/API/getTrend', methods=["POST"])
def getTrend():
    date = json.loads(request.get_data())
    ret = db.SITEGetTrend(date["date"])
    return json.dumps(ret)


@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
