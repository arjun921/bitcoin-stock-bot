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


def fetch_range():
	a = fetch_summary()
	a=a[0]
	stri = str(a)
	s = stri[stri.find('Day\'s Range:'):]
	low = s[s.find('low">')+s[s.find('low">'):].find('>')+1:][:s[s.find('low">')+s[s.find('low">'):].find('>')+1:].find('</span>')]
	high = stri[stri.find('low'):][stri[stri.find('low'):].find('high">'):][stri[stri.find('low'):][stri[stri.find('low'):].find('high">'):].find('>')+1:]
	high = high[:high.find('</span')]
	return low,high


def load_page():
	req = Request('https://in.investing.com/commodities/crude-oil', headers={'User-Agent': 'Mozilla/5.0'})
	webpage = urlopen(req).read()
	return webpage


def fetch_current():
	webpage = ""
	soup = BeautifulSoup(load_page(), 'html.parser')
	x = soup.find_all('span',class_="arial_26 inlineblock pid-8849-last")
	x = str(x[0])
	return x[x.find('>')+1:x.find('</span>')]


def fetch_summary():
	webpage = ""
	soup = BeautifulSoup(load_page(), 'html.parser')
	x = soup.find_all('div',class_="bottomText float_lang_base_1")
	return x


def fetch_open():
	soup = BeautifulSoup(load_page(), 'html.parser')
	y = soup.find_all('div',class_="first inlineblock")
	for x in y:
		stri = str(x)
		if stri.find("Open")>0:
			val = x.find('span',class_="float_lang_base_2 bold").text
	return val


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
	if change_percent.find('+')==0:
		return "UP by " + change_percent
	elif change_percent.find('-')==0:
		return "DOWN by " + change_percent
#     if stri.find('up') > 1:
#         return "UP by " + change_percent
#     elif stri.find('down') > 1:
#         return "DOWN by " + change_percent


@app.route('/webhook', methods=['POST'])
def webhook():
	req = request.get_json(silent=True, force=True)
	print("Request:")
	print(json.dumps(req, indent=4))
	res = makeWebhookResult(req)
	res = json.dumps(res, indent=4)
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r


def makeWebhookResult(req):
	result = req.get("result")
	parameters = result.get("parameters")
    
	if parameters.get("OIL-Price"):
		params = parameters.get("OIL-Price")
		if params == 'current price':
			speech = "The " + params + " is " + str(fetch_current()) + " USD."
		elif params == 'closing price':
			speech = "The " + params + " was " + fetch_close() + " USD."
		elif params == 'opening price':
			speech = "The " + params + " is " + str(fetch_open()) + " USD."
		elif params == 'highest price':
			low,high = fetch_range()
			speech = "Today's highest price is {} USD.".format(high)
		elif params == 'lowest price':
			low,high = fetch_range()
			speech = "Today's lowest price is {} USD.".format(low)

	if parameters.get("market-trend"):
		params = parameters.get("market-trend") 
		if params == 'trend':
			speech = "The " + params.lower() + " is " + fetch_trend()
		elif params == 'range':
			low,high = fetch_range()
			speech = "Today's range is {} - {}".format(low,high)
    


	return {
	"speech": speech,
	"displayText": speech,
	"source": "apiai-onlinestore-shipping"
	}

if __name__ == '__main__':

	port = int(os.getenv('PORT', 5000))
	print("Starting app on port %d" % port)
	app.run(debug=True, port=port, host='0.0.0.0')
