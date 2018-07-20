#!/usr/bin/env python3

import configparser
import json
import sys
import time

import bl3p



def d(j):
	print(json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')))



class MarketMaker:
	def __init__(self, exchange, config):
		self.exchange = exchange
		self.interval    = float(config.get('marketmaker', 'interval'))
		self.minSpread   = float(config.get('marketmaker', 'minSpread'))
		self.fractionBTC = float(config.get('marketmaker', 'fractionBTC'))
		d(exchange.walletHistory('BTC', 10))


	def run(self):
		while True:
			time.sleep(self.interval)
			print('MarketMaker iteration')



config = configparser.RawConfigParser()

if len(sys.argv) == 2:
	config.read(sys.argv[1])
else:
	config.read('marketmaker.cfg')

public_key = config.get('bl3p', 'public_key')
secret_key = config.get('bl3p', 'secret_key')

exchange = bl3p.Bl3pApi('https://api.bl3p.eu/1/', public_key, secret_key)

marketmaker = MarketMaker(exchange, config)
marketmaker.run()

