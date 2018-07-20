#!/usr/bin/env python3

import configparser
import json
import math
import sys
import time

import bl3p



def d(j):
	print(json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')))



class MarketMaker:
	def __init__(self, exchange, config):
		self.exchange = exchange
		self.interval    = float(config.get('marketmaker', 'interval'))

		minSpread   = float(config.get('marketmaker', 'minSpread'))
		fraction    = float(config.get('marketmaker', 'fractionBTC'))
		self.assets = 'EUR', 'BTC'
		self.market = 'BTC'
		self.fractions = 1-fraction, fraction

		#minSpread = mul**2  - 1
		self.multiplier = math.sqrt(1 + minSpread)
		print('Multiplier: ', self.multiplier)

		#TODO: cancel all active orders

		self.balances = 0, 0
		self.updateBalances()
		print('Initial balances: ', self.balances)

		#Make sure we have both currencies (to avoid division by zero)
		#Do this with small market orders
		if self.balances == (0, 0):
			raise Exception('Cannot trade without funds')
		if self.balances[0] == 0:
			amount = int(0.1 * self.fractions[0] * self.balances[1])
			print('We have no %s; market order selling %d in %s' % \
				(self.assets[0], amount, self.assets[1]))
			d(self.exchange.addOrder(self.market, 'ask', order_amount=amount))
		if self.balances[1] == 0:
			amount = int(0.1 * self.fractions[1] * self.balances[0])
			print('We have no %s; market order selling %d in %s' % \
				(self.assets[1], amount, self.assets[0]))
			d(self.exchange.addOrder(self.market, 'bid', order_amount_funds=amount))

		if 0 in self.balances:
			#Wait until something changes
			while not self.updateBalances():
				time.sleep(self.interval)
			print('New balances: ', self.balances)

		print('Implied price of current balances: %f %s/%s' % \
			(
			self.getImpliedPrice() * self.exchange.getBtcMultiplier() / self.exchange.getEurMutiplier(),
			self.assets[0], self.assets[1]))

		#Enter the market
		self.placeBidOrders()
		self.placeAskOrders()


	def run(self):
		while True:
			time.sleep(self.interval)
			print('MarketMaker iteration')


	def updateBalances(self):
		'Return value: indicates whether balances have changed'
		balances = exchange.getBalances()
		newBalances = \
		[
		int(balances['data']['wallets'][c]['balance']['value_int'])
		for c in self.assets
		]
		ret = newBalances != self.balances
		self.balances = newBalances
		return ret


	def placeBidOrders(self):
		currentPrice = self.getImpliedPrice()


	def placeAskOrders(self):
		currentPrice = self.getImpliedPrice()


	def getImpliedPrice(self):
		'Return value: price per satoshi in EUR (*1e5)'
		#value[1] / fraction[1] = value[0] / fraction[0]
		#fraction[0] / fraction[1] = value[0] / value[1]
		#fraction[0] / fraction[1] = amount[0] / (price * amount[1])
		#price * fraction[0] / fraction[1] = amount[0] / amount[1]
		#price = (fraction[1]*amount[0]) / (fraction[0]*amount[1])
		return (self.fractions[1]*self.balances[0]) / (self.fractions[0]*self.balances[1])


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

