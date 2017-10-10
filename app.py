#!/usr/bin/env python

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "oil.current":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    zone = parameters.get("oil-price")

    # cost = {'Current Price':100, 'Closing Price':200, 'Opening Price':300, 'Asia':400, 'Africa':500}

    speech = "The " + zone + " is " + fetch_current() + " USD."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }

def load_page():
    req = Request('https://in.investing.com/commodities/crude-oil', headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    return webpage

def fetch_current():
    soup = BeautifulSoup(load_page(), 'html.parser')
    x = soup.find_all('span',class_="arial_26 inlineblock pid-8849-last")
    return x[0].contents[0]


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
