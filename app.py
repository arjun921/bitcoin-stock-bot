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

    if zone == 'Current Price':
        speech = "The " + zone + " is " + fetch_current() + " USD."
    elif zone == 'Closing Price':
        speech = "The " + zone + " is " + fetch_close() + " USD."
    elif zone == 'Opening Price':
        speech = "The " + zone + " is " + fetch_open() + " USD."
    elif zone == 'Trend':
        speech = "The " + zone.lower() + " is " + fetch_trend()

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-onlinestore-shipping"
    }


def load_page():
    req = Request('https://in.investing.com/commodities/crude-oil', headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    return webpage


def fetch_current():
    webpage = ""
    soup = BeautifulSoup(load_page(), 'html.parser')
    x = soup.find_all('span',class_="arial_26 inlineblock pid-8849-last")
    return x[0].contents[0]


def fetch_summary():
    webpage = ""
    soup = BeautifulSoup(load_page(), 'html.parser')
    x = soup.find_all('div',class_="bottomText float_lang_base_1")
    return x


def fetch_open():
    a = fetch_summary()
    a = a[0]
    stri = str(a)
    s = stri[stri.find('Open:</span> <span dir="ltr">'):]
    open_ = s[s.find('"ltr">')+6:s.find('</span></li>\n<li><span class="lighterGrayFont noBold">')]
    return open_


def fetch_close():
    a = fetch_summary()
    a = a[0]
    stri = str(a)
    return stri[stri.find('ltr') + 5:stri.find('</span>', stri.find('ltr'))]


def fetch_trend():
    webpage = ""
    soup = BeautifulSoup(load_page(), 'html.parser')
    x = soup.find_all('div', class_="instrumentDataFlex")
    stri = str(x[0])
    pctage = x[0].find_all('span', class_="parentheses")
    strpctage = str(pctage)
    change_percent = strpctage[strpctage.find('>') + 1:strpctage.find('%') + 1]
    if stri.find('up') > 1:
        return "UP by " + change_percent
    elif stri.find('down') > 1:
        return "DOWN by " + change_percent


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=True, port=port, host='0.0.0.0')
