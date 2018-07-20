#!/usr/bin/env python3

import configparser
import json
import math
import sys
import time

import bl3p



def d(j):
	print(json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')))



class Order:
	def __init__(self, amount_funds, price):
		self.amount_funds = amount_funds
		self.price = price



class MarketMaker:
	def __init__(self, exchange, config):
		self.exchange = exchange
		self.interval    = float(config.get('marketmaker', 'interval'))
		self.numOrders   = int(config.get('marketmaker', 'numOrders'))

		minSpread   = float(config.get('marketmaker', 'minSpread'))
		fraction    = float(config.get('marketmaker', 'fractionBTC'))
		self.assets = 'EUR', 'BTC'
		self.market = 'BTC'
		self.fractions = 1-fraction, fraction

		#minSpread = mul**2  - 1
		self.multiplier = math.sqrt(1 + minSpread)
		print('Multiplier: ', self.multiplier)

		#Cancel all active orders
		result = self.exchange.getAllActiveOrders(self.market)
		assert result['result'] == 'success'
		order_ids = [order['order_id'] for order in result['data']['orders']]
		for id in order_ids:
			result = self.exchange.cancelOrder(self.market, id)
			assert result['result'] == 'success'

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

		print('Implied price of current balances: ',
			self.printablePrice(self.getImpliedPrice()))

		#Enter the market
		self.bidOrders = []
		self.askOrders = []
		self.placeBidOrders()
		self.placeAskOrders()


	def run(self):
		while True:
			time.sleep(self.interval)
			print('MarketMaker iteration')


	def updateBalances(self):
		'Return value: indicates whether balances have changed'
		result = exchange.getBalances()
		newBalances = \
		[
		int(result['data']['wallets'][c]['balance']['value_int'])
		for c in self.assets
		]
		ret = newBalances != self.balances
		self.balances = newBalances
		return ret


	def placeBidOrders(self):
		print('Placing BID orders')
		price = self.getImpliedPrice()
		oldBalances = self.balances
		multiplier = self.multiplier
		print('Implied price: ', self.printablePrice(price))

		for i in range(self.numOrders):
			price /= multiplier
			multiplier = multiplier ** 2 #Double the step size the next time

			#Prevent underflow
			if price < 1e-100:
				break

			totalValue = oldBalances[0] + price * oldBalances[1]
			newBalances = self.fractions[0] * totalValue, self.fractions[1] * totalValue / price

			amount_funds = int(oldBalances[0] - newBalances[0])
			print('Order: price %s, funds amount %d' % (self.printablePrice(price), amount_funds))
			self.placeBidOrder(Order(amount_funds=amount_funds, price=price))

			oldBalances = newBalances


	def placeAskOrders(self):
		print('Placing ASK orders')
		price = self.getImpliedPrice()
		oldBalances = self.balances
		multiplier = self.multiplier
		print('Implied price: ', self.printablePrice(price))

		for i in range(self.numOrders):
			price *= multiplier
			multiplier = multiplier ** 2 #Double the step size the next time

			#Prevent overflow
			if price > 1e100:
				break

			totalValue = oldBalances[0] + price * oldBalances[1]
			newBalances = self.fractions[0] * totalValue, self.fractions[1] * totalValue / price

			amount_funds = int(newBalances[0] - oldBalances[0])
			print('Order: price %s, funds amount %d' % (self.printablePrice(price), amount_funds))
			self.placeAskOrder(Order(amount_funds=amount_funds, price=price))

			oldBalances = newBalances


	def placeBidOrder(self, order):
		self.placeOrder(order, 'bid', self.bidOrders)


	def placeAskOrder(self, order):
		self.placeOrder(order, 'ask', self.askOrders)


	def placeOrder(self, order, typeName, orderList):
		while True:
			result = self.exchange.addOrder(self.market, typeName,
				order_amount_funds=order.amount_funds,
				order_price=int(order.price * self.exchange.getBtcMultiplier()))
			d(result)
			if result['result'] == 'success':
				break
			print('%s order placement failed; retrying' % typeName)
			time.sleep(10 * self.interval)

		order.id = result['data']['order_id']
		orderList.append(order)


	def getImpliedPrice(self):
		'Return value: price per satoshi in EUR (*1e5)'
		#value[1] / fraction[1] = value[0] / fraction[0]
		#fraction[0] / fraction[1] = value[0] / value[1]
		#fraction[0] / fraction[1] = amount[0] / (price * amount[1])
		#price * fraction[0] / fraction[1] = amount[0] / amount[1]
		#price = (fraction[1]*amount[0]) / (fraction[0]*amount[1])
		return (self.fractions[1]*self.balances[0]) / (self.fractions[0]*self.balances[1])


	def printablePrice(self, price):
		return '%s %s/%s' % (
			price * self.exchange.getBtcMultiplier() / self.exchange.getEurMutiplier(),
			self.assets[0], self.assets[1])


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

