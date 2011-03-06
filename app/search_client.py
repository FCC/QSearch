#!/usr/bin/env python
# encoding: utf-8
# Get redis-py from https://github.com/andymccurdy/redis-py
"""
search_client.py

Use web.py to create a simple web client for search API lookups
> python search_client.py 8081

Created by Greg Elin on 2011-1-30.
Copyright (c) 2011 Greg Elin. All rights reserved.
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
	'/(.*)/', 'search_client',
	'/(.*)', 'search_client'
	)

render = web.template.render('webpytemplates/', cache=False)
app = web.application(urls, globals())

#  Set up molds for different content types
global molds
molds = {
	'acronym': ['name', 'definition'],
	'callsign': ['1363569', '569360', '1', '0.0', 'city', 'state', 'B', '0.0', 'callsign', '5360', 'company', '', 'N', 'N', 'N', 'N', 'N', 'Y', 'N', 'N', '', '100.0', 'date', '']
	}

class search_client:
	# Consumes the Restful json_api (/>json) API
	def GET(self,term):
		result = ""
		key = ""
		raw = ""
		f = urllib2.urlopen('http://localhost:8080/search/'+term+"/>json")
		result = f.read(10000)
		raw = result
		result = result.replace("&quot;",'"')
		result = result.replace("&#39;",'"')
		r2 = json.loads(result)
		value = r2
		result2 = ""
		if 'acronym' in r2:
			key = "acronym "+term
			value = r2['acronym']
			return render._acronym(term,value)
		if 'callsign' in r2:
			key = "Callsign "+term
			value = r2['callsign']
			return render._callsign(term,value)
		return render.search_client(term,result,key,raw)

web.webapi.internalerror = web.debugerror

if __name__ == "__main__":
    app.run()
