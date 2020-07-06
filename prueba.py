import logging
from time import sleep

import poloniex
import self as self
from poloniex import Poloniex


class Trader(object):
    logging.basicConfig()
    poloniex.logger.setLevel(logging.DEBUG)

    self.api_key = '38C0ZK18-HF6D9X18-5T3WRAD2-H1QMZTDT'
    self.api_secret = '086b6d6d87740c3676fcc909b3c4affe301ea3d522c1942564f037bae3e3168bd23e8d8e1c6a8127d1202ba75b7d5af6103d1bc54d0d082c8bdd51dac865fd17'

    self.polo = Poloniex(self.api_key, self.api_secret)
    ticker = self.polo.returnTicker()['USDT_BTC']
    print(ticker)
    print(ticker['lowestAsk'])
    #help(self.polo)
    print(self.polo.returnOpenOrders(currencyPair='USDT_BTC'))
    #print(self.polo.returnBalances())
    rate = 9077.86192412 - 100
    amount = 30/rate
    #self.polo.buy(currencyPair='USDT_BTC', rate=rate, amount=amount)
    print(self.polo.returnFeeInfo())

    print(self.polo('returnTicker'))

    def on_ticker(self,data):
        print(data)
    #
    # sock = poloniex.PoloniexSocketed()
    #
    # sock.startws(subscribe={'ticker': on_ticker})
    # sleep(10)
    # sock.stopws()

    print(self.polo.marketTradeHist(currencyPair='USDT_BTC'))



