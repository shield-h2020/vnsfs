#!/usr/bin/python
#  -*- coding: utf8 -*-
from flask import Flask, request
from api.base import base
from api.html import html
from api.v1 import v1
from api.v2 import v2


app = Flask(__name__)
app.register_blueprint(base)
app.register_blueprint(html)
app.register_blueprint(v1)
app.register_blueprint(v2)


@app.route('/set', methods=['POST'])
def set():
    json_data = request.get_json()
    print(json_data)
    return "Flow created!"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8082, threaded=True)
