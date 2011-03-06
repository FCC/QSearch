#!/usr/bin/env python
# encoding: utf-8
# Get redis-py from https://github.com/andymccurdy/redis-py
"""
etl_fccphone_json.py

Convert pipe delimited phone book info to json file
Created by Greg Elin on 2011-02-05.
Copyright (c) 2011 Greg Elin. All rights reserved.
"""

import sys
import getopt
import csv
import json
import redis

global r
r = redis.Redis(host='localhost', port=6379, db=0)


class ETL():
	"""A class to load a key-value pair csv file into Redis
	
	"""
	
	def __init__(self, srcfile, delimiter=',', quotechar='"', verbose=False, debug=False, key=0, prefix='', target=''):
		# Set attributes to parameters
		self.srcfile = srcfile
		self.delimiter = delimiter
		self.quotechar = quotechar
		self.verbose = verbose
		self.debug = debug
		self.key = int(key)
		self.prefix = prefix
		self.target = target
		
		# Verbose?
		if (self.verbose):
			print "delimiter: %s" % self.delimiter
			print "verbose: %s" % self.verbose
			print "debug: %s" % self.debug
			
		# Start gathering info
		self.entries = self.csv_read()
		# self.count = self.len()

	def csv_read(self):
		try:
			if (self.verbose): print "srcfile: Read file '%s'" % self.srcfile
			reader = csv.reader(open(self.srcfile, 'rb'), delimiter=self.delimiter, quotechar=self.quotechar)
			entries = []
			row_json = {}
			cnt = 0
			
			for row in reader:
				# REALLY important to remove trailing spaces for key, so let's strip for all values at same time
				row = [str(val).strip() for val in row]
				cnt +=1 
				# print "%d trying to load %s, %s" % (cnt,row, row[self.key])
				key = self.prefix + ":" + row[self.key].strip()
				my_json = self.array_json(self.prefix,row[self.key],row,self.prefix )
				my_json['id'] = row[self.key]
				if (self.verbose): print "%s %s\n" % (key,my_json)
				# Be sure to use json.dumps to make serialized object a correct string
				r.set(key,json.dumps(my_json))
				entries.append(row)
			self.srcfileparsed = True
			return entries
		except:
			print "\n** Error reading source file '%s'\n" % self.srcfile
			self.srcfileparsed = False

	def array_json(self, key, key_value, values, mold):
		# Return a json object 
		mold = molds[mold]
		# Apply mold to datahandler
		md = datahandler(values).mold(mold)
		return md
		
	def len(self):
		# if (self.verbose): print "srcfile entries: %d" % len(self.entries)
		return self.entries.__len__()




global molds
molds = {
	'docket': ['name','unknown','type','nameagain','link','desc','comment'],
	'fccperson': ['last_name', 'first_name','bo','phone','email'],
	'callsign': ['1363569', '569360', '1', '0.0', 'city', 'state', 'B', '0.0', 'callsign', '5360', 'company', '', 'N', 'N', 'N', 'N', 'N', 'Y', 'N', 'N', '', '100.0', 'date', '']
	}

class datahandler():
	"""Data Handler

	"""

	def __init__(self, init_values):
		# Setup
		self.init_values = init_values 
		self.values = self.init_values

	def mold(self,mold_features):
		# Return a dictionary of the molded data
		molded = {}
		fieldindex = 0
		for feature in mold_features:
			molded[feature] = self.values[fieldindex]
			fieldindex += 1
		return molded
		# return json.dumps(molded)

	def mold_empty(self,mold_features):
		molded = {}
		for feature in mold_features:
			molded[feature] = "Empty"
		return molded

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

help_message = '''
Load a key-value pair comma delimited set of values into memcache.

Make sure memcache is running
$ memcached -vv

Options:
	-h             Print this help
	-f, --file     Source key-value pair file to parse
	-t, --target file	Target file of json rows
	-l, --delimiter	Delimiter (options: , \t ' ' |)
	-v, --verbose  Verbose output
	-d, --debug    Debug output 
	-k, --key      Set column index to use as unique key
	-p, --prefix   Set prefix to add to key (person:thekey)

Examples:
	python etl_fccphone_json.py -v -l "|" -k 0 -p fccperson -f /Volumes/fccdisk/codedata/data/enterprise/phonebook.txt
'''

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hof:t:l:vdk:p:", ["help", "output=", "file=", "target=", "delimiter=" "verbose", "debug", "key=", "prefix="])
		except getopt.error, msg:
			raise Usage(msg)

		# option processing
		_verbose = False
		_debug = False
		_delimiter = ","
		_key = 0
		_prefix = ""
		_target = ""

		for option, value in opts:
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-v", "--verbose"):
				_verbose = True
			if option in ("-d", "--debug"):
				_debug = True
			if option in ("-l", "--delimiter"):
				if value in [',','\t',' ','|']:
					_delimiter = value
			if option in ("-k", "--key"):
				_key = value
			if option in ("-p", "--prefix"):
				_prefix = value
			if option in ("-t", "--target"):
				_target = value
			if option in ("-f", "--file"):
				srcfile = value
				loader = ETL(srcfile, verbose=_verbose, delimiter=_delimiter, debug=_debug, key=_key, prefix=_prefix, target=_target)

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2


if __name__ == "__main__":
	sys.exit(main())
