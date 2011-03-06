#!/usr/bin/env python
# encoding: utf-8
# Get redis-py from https://github.com/andymccurdy/redis-py
"""
qsearch_redis.py

Use web.py to create a simple web form for processing Redis lookups:

	$ python qsearch_redis.py 8080

Command Line Testing:

	$ curl http://localhost:8080/search/json/WIAT | python -mjson.tool

License:
	Publice Domain
	Created by Greg Elin for Federal Communication Commission
"""

import redis
import web
import time
import urllib2
import json

# Establish link to memchached server
global r
r = redis.Redis(host='localhost', port=6379, db=0)

# Register routes for web server using regex
urls = (
	'/lookup/(.*)/', 'lookup',
	'/lookup/(.*)', 'lookup',
	'/search/json/(.*)/', 'search_json',
	'/search/json/(.*)', 'search_json',
	'/search/jsonp/(.*)', 'search_jsonp',
	'/search/(.*)/>jsonp', 'search_jsonp',
	'/search/(.*)/>json', 'search_json',
	'/search/(.*)/', 'search',
	'/search/(.*)', 'search'
	)

render = web.template.render('webpytemplates/', cache=False)
app = web.application(urls, globals())

#  Set up molds for different content types
global molds
molds = {
	'acronym': ['name', 'definition'],
	'callsign': ['1363569', '569360', '1', '0.0', 'city', 'state', 'B', '0.0', 'callsign', '5360', 'company', '', 'N', 'N', 'N', 'N', 'N', 'Y', 'N', 'N', '', '100.0', 'date', ''],
	}
	
# molds_html = {
# 	'callsign': 
# }

class lookup:
	def GET(self, term):
		return render.lookup(term)
	
class search:
	# Performs a basic search and displays an HTML page
	def GET(self, term):
		debug = ""
		my_time = time.asctime( time.localtime(time.time()) )
		if not term:
			result = "Please append a term to lookup, e.g., localhost/json/docket:08-51"
			return render.help()
		else:
			# Loop through molds
			result = {}
			for mold in molds:
				mold_key = mold+":"+term
				debug += mold_key+"; "
				mold_key_upper = mold+":"+term.upper()
				debug += mold_key_upper+"; "
				lookup = r.get(mold_key.encode('utf-8'))
				if (lookup):
					result[mold] = lookup
				lookup = r.get(mold_key_upper.encode('utf-8'))
				if (lookup):
					result[mold] = lookup
			return render.search(my_time, term, result, debug.encode('utf-8'))

class search_json:
	# Provides a restful API using json
	def GET(self, term):
		debug = ""
		my_time = time.asctime( time.localtime(time.time()) )
		if not term:
			result = "Please append a term to lookup, e.g., localhost/json/docket:08-51"
		else:
			result = {}
			for mold in molds:
				mold_key = mold+":"+term
				mold_key_upper = mold+":"+term.upper()
				debug += mold_key+"; "+mold_key_upper+"; "
				lookup = r.get(mold_key.encode('utf-8'))
				if (lookup): result[mold] = lookup
				lookup = r.get(mold_key_upper.encode('utf-8'))
				if (lookup): result[mold] = json.loads(lookup)
			web.header('Content-Type', 'application/json')
			return json.dumps(result)

class search_jsonp:
	# Provides a restful API using json
	def GET(self, term):
		debug = ""
		# Access the query parameters. If none found, set to value 'callback'
		query_string = web.ctx.env.get('QUERY_STRING').split("&")
		params = {}
		for param in query_string:
			kv = param.split("=")
			if (len(kv) == 2):
				params[str(kv[0]).lower()] = str(kv[1])
		if 'callback' in params: 
			callback = params['callback']
		else:
			callback = "callback"
		my_time = time.asctime( time.localtime(time.time()) )
		if not term:
			result = "Please append a term to lookup, e.g., localhost/json/docket:08-51"
		else:
			result = {}
			for mold in molds:
				mold_key = mold+":"+term
				mold_key_upper = mold+":"+term.upper()
				debug += mold_key+"; "+mold_key_upper+"; "
				lookup = r.get(mold_key.encode('utf-8'))
				if (lookup): result[mold] = lookup  # should this be json.loads(lookup), too?
				lookup = r.get(mold_key_upper.encode('utf-8'))
				if (lookup): 
					result[mold] = json.loads(lookup)
					result["type"] = mold
					result["html"] = mold_html(term,result)
			web.header('Content-Type', 'application/json')
			my_jsonp = "%s(%s)" % (callback,json.dumps(result))
			return my_jsonp

def mold_html(term,result):
	# Defines simple HTML snippet templates for server-side driven display of human-readable result
	html = ""
	if 'acronym' in result:
		html += "<div id=\"qsearch_result\">%s: %s</div>" % (result["acronym"]["name"],result["acronym"]["definition"])
	if 'callsign' in result:
		html += "<div id=\"qsearch_result\">CALLSIGN <b>%s</b> licensed to %s in %s, %s</div>" % (result["callsign"]["callsign"],result["callsign"]["company"],result["callsign"]["city"],result["callsign"]["state"])
	return html

		
web.webapi.internalerror = web.debugerror
if __name__ == "__main__":
    app.run()
