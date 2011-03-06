#!/usr/bin/env python
# encoding: utf-8
# Get redis-py from https://github.com/andymccurdy/redis-py
"""
redisloadx.py

Enhanced memloadx.py targeting redis in-memory database
Created by Greg Elin on 2011-01-31.
Copyright (c) 2011 Greg Elin. All rights reserved.
"""

import sys
import getopt
import csv
import redis

global r
r = redis.Redis(host='localhost', port=6379, db=0)

class RedisLoad():
	"""A class to load a key-value pair csv file into Redis
	
	"""
	
	def __init__(self, srcfile, delimiter=',', quotechar='"', verbose=False, debug=False, key=0, prefix=''):
		# Set attributes to parameters
		self.srcfile = srcfile
		self.delimiter = delimiter
		self.quotechar = quotechar
		self.verbose = verbose
		self.debug = debug
		self.key = int(key)
		self.prefix = prefix
		
		# Verbose?
		if (self.verbose):
			print "delimiter: %s" % self.delimiter
			print "verbose: %s" % self.verbose
			print "debug: %s" % self.debug
			
		# Start gathering info
		self.entries = self.csv_read()
		# self.count = self.len()
		
		# Load memcache
		# self.load()

	def csv_read(self):
		try:
			if (self.verbose): print "srcfile: Read file '%s'" % self.srcfile
			reader = csv.reader(open(self.srcfile, 'rb'), delimiter=self.delimiter, quotechar=self.quotechar)
			# entries = [entry for entry in reader]
			entries = []
			cnt = 0
			for row in reader:
				# REALLY important to remove trailing spaces for key, so let's strip for all values at same time
				row = [str(val).strip() for val in row]
				cnt +=1 
				print "%d trying to load %s, %s" % (cnt,row, row[self.key])
				# r.set(row[self.key.strip(),row) # Store an array
				key = self.prefix + ":" + row[self.key].strip()
				r.set(key,"|".join(row)) # Store pipe delimited string
				# self.load_row(row) # put this back in
				entries.append(row)
			self.srcfileparsed = True
			return entries
		except:
			print "\n** Error reading source file '%s'\n" % self.srcfile
			self.srcfileparsed = False

	def len(self):
		# if (self.verbose): print "srcfile entries: %d" % len(self.entries)
		return self.entries.__len__()
	
	def load_row(self,row):
		try:
			print "load %s : %s" % (row[self.key],"|".join(row))
			# r.set(row[self.kv[0]],row[self.kv[1]])
			# r.set(row[self.key],"|".join(row).trim())
			r.set(str("x"),"|".join(row).trim())
			# r.set(row[self.key,row)
		except:
			if (self.verbose): print "Error caching %s:: %s" % (row[self.kv[0]],"|".join(row))
			pass
		
	def load(self):
		for entry in self.entries:
			try:
				print "entry %s | %s : %s" % (entry,entry[self.kv[0]],entry[self.kv[1]])
				# r.set(entry[0],entry[1])
				r.set(entry[self.kv[0]],entry[self.kv[1]])
			except:
				print "error"
				pass
			#	if (self.debug): print "Error caching [%s, %s]" % (entry[0],entry[1])
		if (self.verbose): print "memcached: loaded"	

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
	-l, --delimiter	Delimiter (options: , \t ' ' |)
	-v, --verbose  Verbose output
	-d, --debug    Debug output 
	-k, --key      Set column index to use as unique key
	-p, --prefix   Set prefix to add to key (person:thekey)

Examples:
	NOTE: pair value is not yet implemented on command line!  must change in code
	python redisloadx.py -f /codedata/data/datahash/search_word_rank.csv
	python redisloadx.py -v -l "|" -f /codedata/data/FCC/public/danilo-ownership/ownership_other_int_xml_data_sample.dat
	python redisloadx.py -v -l "|" -f /codedata/data/FCC/public/danilo-ownership/call_sign_history.txt
	python redisloadx.py -f /codedata/data/datahash/search_word_rank.csv
	python redisloadx.py -v -l "|" -f /codedata/data/FCC/public/danilo-ownership/ownership_other_int_xml_data_sample.dat
	python redisloadx.py -v -l "|" -f /codedata/data/FCC/public/danilo-ownership/call_sign_history.txt [does not work]
	python redisloadx.py -v -l "|" -k 0 -p docket -f /codedata/data/datahash/hotdockets.txt 
	

'''

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hof:l:vdk:p:", ["help", "output=", "file=", "delimiter=" "verbose", "debug", "key=", "prefix="])
		except getopt.error, msg:
			raise Usage(msg)

		# option processing
		_verbose = False
		_debug = False
		_delimiter = ","
		_key = 0
		_prefix = ""

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
			if option in ("-f", "--file"):
				srcfile = value
				loader = RedisLoad(srcfile, verbose=_verbose, delimiter=_delimiter, debug=_debug, key=_key, prefix=_prefix)

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2


if __name__ == "__main__":
	sys.exit(main())
