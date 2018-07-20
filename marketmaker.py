#!/usr/bin/env python3

import configparser
import json
import sys

import bl3p



def d(j):
	print(json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')))

# example:
config = configparser.RawConfigParser()

if len(sys.argv) == 2:
	config.read(sys.argv[1])
else:
	config.read('bl3p.cfg')

public_key = config.get('bl3p', 'public_key') # ........-....-....-....-............
secret_key = config.get('bl3p', 'secret_key') # (long string with a-z/A-Z/0-9 and =)

b = bl3p.Bl3pApi('https://api.bl3p.eu/1/', public_key, secret_key)

d(b.walletHistory('BTC', 10))

