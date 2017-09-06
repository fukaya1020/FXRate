# -*- coding: utf-8 -*-
import traceback
import re
import sys
import json
import urllib2
from collections import OrderedDict
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime as dt
from datetime import timedelta
from flask_bootstrap import Bootstrap
app = Flask(__name__)
Bootstrap(app)

yql_url = "https://query.yahooapis.com/v1/public/yql"


def convert_time(mmddyyyy, hhmm):
	try:
		time_str = mmddyyyy + u' ' + hhmm.upper()
		tdate = dt.strptime(time_str, '%m/%d/%Y %I:%M%p')
		tdate += timedelta(hours = 8)
		yyyymmdd = tdate.strftime('%Y/%m/%d %H:%M')
		return yyyymmdd
	except:
		print(traceback.format_exc())
		return None


def parse_yql_json(html_src):
	json_loads = json.loads(html_src)
	out_doc = OrderedDict()
	result_root = json_loads['query']
	rate_root = result_root['results']['rate']

	ret_dic = OrderedDict()
	for dict in rate_root:
		data_doc={}
		id_name = dict['id']
		data_doc['id'] = dict['id']
		data_doc['Rate'] = dict['Rate']
		data_doc['Time'] = convert_time(dict['Date'], dict['Time'])
		ret_dic[id_name] = data_doc
	return ret_dic


def get_data_from_yql():
	try:
		# YQLをAPI経由で利用します
		params = 'q=select * from yahoo.finance.xchange where pair in ("USDJPY,EURJPY,GBPJPY,AUDJPY,NZDJPY,CADJPY,CHFJPY,ZARJPY")'.replace(' ', '%20').replace('"', '%22')
		params += '&format=json'
		params += '&env=store://datatables.org/alltableswithkeys'.replace(':', '%3A').replace('/', '%2F')
		url = yql_url + "?" + params
		print(url)
		req = urllib2.Request(url)
		res = urllib2.urlopen(req)
		res_src = res.read()
		ret_data = parse_yql_json(res_src)
		return ret_data
	except:
		print(traceback.format_exc())
		return None


@app.route("/", methods=['GET'])
def main():
	rate_data = get_data_from_yql()
	list_rd = list(rate_data)
	print(rate_data)

	for i, x in enumerate(rate_data):
		print(rate_data[x])
	
	return render_template('index.html', fxdata=rate_data)


if __name__ == '__main__':
	main(debug=True)
