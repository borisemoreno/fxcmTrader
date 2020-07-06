import matplotlib.pyplot as plt
import numpy as np
import time
from poloniex import Poloniex
import datetime
import os
from functools import reduce


def add_to_file(file, idate, iopen, iclose, iaverage):
    file.write(
        str(idate) + "," + str(float(iopen)) + "," + str(float(iclose)) + "," + str(float(iaverage)) + "\r\n")


def append_to_file(filename, indate, inopen, inclose, inaverage):
    print("append_to_file:" + filename)
    file3 = open(filename + ".txt", "a")
    add_to_file(file3, indate, inopen, inclose, inaverage)
    file3.close


class Trader(object):
    """Trader
    """

    def __init__(self):
        self.api_key = '38C0ZK18-HF6D9X18-5T3WRAD2-H1QMZTDT'
        self.api_secret = '086b6d6d87740c3676fcc909b3c4affe301ea3d522c1942564f037bae3e3168bd23e8d8e1c6a8127d1202ba75b7d5af6103d1bc54d0d082c8bdd51dac865fd17'
        self.seeding = True
        self.prevTrend = 'BAJADA'
        self.trend = ''
        self.oldTrend = ''
        self.strength = 0
        self.walletUSD = float(25.00000)
        self.walletBTC = float(0.00000)
        self.tradingFee = 0.00125
        self.lastBuy = 0.00000
        self.lastSell = 0.00000
        self.buyPrice = 0.00000
        self.sellPrice = 0.00000
        self.MINORDERBASE = 25
        self.MINORDERASSET = 0.00005
        self.ORDERAMOUNT = 25.0
        self.simPercent = 95  # 75
        self.sampleSize = 20  # 20
        self.ma20 = []
        self.rawDate = []

        self.training = True
        self.totalStart = time.time()

        self.lsymbol = "USDT_BTC"
        # lperiod = "1h"
        self.lperiod = 300
        self.lexchange = "poloniex"
        self.lrefresh = 5  # minutes
        self.filename = self.lexchange + self.lsymbol + str(self.lperiod)

        # initialize the poloniex api
        self.polo = Poloniex(self.api_key, self.api_secret)

        self.orders = []

        # ticker = polo.returnTicker()['USDT_BTC']
        # print(ticker)
        #
        # balances = polo.returnBalances()
        # print(balances)
        #
        # help(self.polo)

    def openfile(self):
        file = open(self.filename + ".txt", "w")
        try:
            os.remove(self.filename + "trans.txt")
        except Exception as e:
            print
            e

        # startValue = 1483236000

        # lastValue = 1483236000
        today = datetime.datetime.now()
        datem = datetime.datetime(today.year, today.month, today.day, today.hour)
        # timestamp = (datem - datetime.datetime(2015, 1, 1)).total_seconds()
        timestamp = datetime.datetime(2020, 4, 1).timestamp()
        # startValue = int(datetime.datetime.utcnow().timestamp()) - 86400*1000
        startValue = timestamp
        lastValue = startValue
        endValue = int(datetime.datetime.utcnow().timestamp())
        print(startValue)
        print(endValue)

        while startValue < endValue:
            print("entrado while")
            print(startValue, endValue)
            tempEndValue = startValue + 86400 * 100

            klines = self.polo.returnChartData(self.lsymbol, self.lperiod, start=startValue, end=tempEndValue)
            # klines = self.polo.returnChartData(self.lsymbol, self.lperiod)

            for kline in klines:
                print("kline-->", lastValue, kline['date'])
                print(datetime.datetime.utcfromtimestamp(kline['date']).strftime('%Y-%m-%dT%H:%M:%SZ'))
                if lastValue < kline['date']:
                    lastValue = kline['date']
                    # hora = time.gmtime(kline['date'] / 1000.)
                    # print (time.strftime('%Y-%m-%d %H:%M:%S',hora), kline['open'])
                    # print(kline)
                    add_to_file(file, kline['date'], kline['open'], kline['close'], kline['weightedAverage'])
                    # file.write(str(kline['date']) + "," + str(float(kline['open'])) + "," + str(float(kline['close'])) + "," + str(float(kline['weightedAverage'])) + "\r\n")

                if kline['date'] > startValue:
                    startValue = kline['date']

                if startValue + 86400 >= endValue:
                    startValue = endValue

        file.close()

    def convert_date(date_bytes):
        print
        date_bytes
        return datetime.timedelta(seconds=int(date_bytes))

    def convert_number(num_bytes):
        print
        num_bytes
        return int(num_bytes)

    def loadData(self):
        tdate, self.bid, self.ask, self.volume = np.genfromtxt(self.filename + '.txt', unpack=True, delimiter=',')
        x = 0
        temp = (self.bid + self.ask) / 2
        xx = 1
        while xx < len(temp):
            if xx >= self.sampleSize:
                self.ma20.append(reduce(lambda x, y: x + y, temp[xx - self.sampleSize: xx]) / self.sampleSize)
            else:
                self.ma20.append(reduce(lambda x, y: x + y, temp[0: xx]) / xx)
            # print (xx, temp[xx-1],"-->",self.ma20[xx-1] )
            xx += 1

        nDate = []
        while x < len(tdate):
            # print("date_convert-->",datetime.datetime.fromtimestamp(tdate[x]))
            nDate.append(datetime.datetime.fromtimestamp(tdate[x]))
            x += 1
        self.rawDate = tdate
        self.date = np.array(nDate)

    def recordTransaction(self, fecha, monto, precio, transaccion):
        file2 = open(self.filename + "trans.txt", "a")
        file2.write(fecha.strftime("%Y%m%d %H%M%S") + "," + str(monto) + "," + str(precio) + "," + transaccion + "\r\n")
        file2.close()

    def buyBTC(self, price):
        print('comprando')
        global walletUSD, walletBTC, seeding
        self.sellPrice = 0
        # self.buyPrice = self.ask[self.toWhat]
        self.buyPrice = price
        # amount = self.walletUSD / self.buyPrice * (1 - self.tradingFee)
        amount = self.walletUSD / self.buyPrice

        if self.seeding:

            if amount > 0:
                self.walletBTC = amount

                self.walletUSD = 0
        else:
            ticker = self.polo.returnTicker()['USDT_BTC']
            self.buyPrice = ticker['lowestAsk'] + 0.1
            # amount = int(amount * 10000.0000) / 10000.0000
            amount = self.walletUSD / self.buyPrice
            print('buy amount:', amount)
            if amount > self.MINORDERASSET:
                try:
                    # rest_client = BinanceRESTAPI(api_key, secret_key)
                    # rest_client.new_order(symbol="BTCUSDT", side="BUY", type="MARKET", quantity=amount)
                    self.polo.buy(currencyPair='USDT_BTC', rate=self.buyPrice, amount=amount)
                except Exception as e:
                    print("Excepcion")
                    print
                    e

            # self.recordTransaction(self.date[self.toWhat], self.ask[self.toWhat], amount, 'BUY')
        # self.waitPeriods=self.sampleSize

    def sellBTC(self, price):

        global walletBTC, walletUSD, seeding
        print('vendiendo')
        # self.sellPrice = self.bid[self.toWhat]
        self.sellPrice = price
        self.buyPrice = 0

        if self.seeding:
            amount = self.walletBTC * (1 - self.tradingFee)
            if amount > 0:
                self.walletBTC = 0

                self.walletUSD = self.sellPrice * amount
        else:
            # amount = int(self.walletBTC * 10000.0000) / 10000.0000
            amount = self.walletBTC

            ticker = self.polo.returnTicker()['USDT_BTC']
            self.sellPrice = ticker['highestBid'] - 0.1

            print('sell amount', amount)
            if amount > self.MINORDERASSET:
                try:
                    # rest_client = BinanceRESTAPI(api_key, secret_key)
                    # rest_client.new_order(symbol="BTCUSDT", side="SELL", type="MARKET", quantity=amount)
                    self.polo.sell(currencyPair='USDT_BTC', rate=self.sellPrice, amount=amount)
                except Exception as e:
                    print("Excepcion")
                    print
                    e
            # self.recordTransaction(self.date[self.toWhat], self.bid[self.toWhat], amount, 'SELL')

        # self.waitPeriods = self.sampleSize

    # def percentChange(self, startPoint, currentPoint):
    #     temp = abs(currentPoint/startPoint)
    #     if np.isnan(temp):
    #         return 0
    #     else:
    #         return abs(1 - temp)

    def percentChange(self, startPoint, currentPoint):
        try:
            if startPoint > currentPoint:
                primero = startPoint
                segundo = currentPoint
            else:
                primero = currentPoint
                segundo = startPoint

            # print("puntos",startPoint,currentPoint)
            x = (abs(primero - segundo) / abs(primero)) * 100.00
            # print("x",x)
            if x == 0.0:
                return 0.000000001
            else:
                return x
        except:
            return 0.000000001

    def mov_avg(x, w):
        for m in range(len(x) - (w - 1)):
            yield sum(np.ones(w) * x[m:m + w]) / w

    def patternStorage(self):
        startTime = time.time()

        # print('len(avgLine)-->', len(self.avgLine))
        x = len(self.avgLine)
        y = self.sampleSize
        currentStance = 'none'

        while y < x:
            pattern = []
            # fPattern = []

            i = 0
            while i < self.sampleSize:
                pattern.append(
                    self.percentChange(self.avgLine[y - self.sampleSize], self.avgLine[y - self.sampleSize + i]))
                i += 1
            # print("pattern",pattern)
            # if (y < len(self.avgLine)-self.sampleSize):
            #     i = 0
            #     while i < self.sampleSize:
            #         fPattern.append(self.percentChange(self.avgLine[y], self.avgLine[y + i]))
            #         i += 1

            # outcomeRange = self.avgLine[y:y + 10]

            currentPoint = self.avgLine[y]

            try:
                # avgOutcome = reduce(lambda x, y: x + y, outcomeRange) / len(outcomeRange)
                # futureOutcome = self.percentChange(currentPoint, avgOutcome)
                futureOutcome = self.percentChange(self.avgLine[y - self.sampleSize], self.avgLine[y + self.sampleSize])
            except Exception as e:
                print(str(e))
                avgOutcome = 0
                futureOutcome = 0

            self.patternAr.append(pattern)
            # self.fPatternAr.append(fPattern)
            self.performanceAr.append(futureOutcome)

            y += 1

        endTime = time.time()
        print('Pattern storing took:', endTime - startTime)

    def currentPattern(self):
        mostRecentPoint = self.avgLine[-1]
        # print('mostRecentPoint-->', mostRecentPoint)
        # print("self.avgLine",self.avgLine)
        i = 0
        while i < self.sampleSize:
            self.patForRec.append(
                self.percentChange(self.avgLine[0 - self.sampleSize], self.avgLine[0 - self.sampleSize + i]))
            i += 1
        # print("patForRec",len(self.patForRec),self.patForRec)
        i = 0
        while i < self.sampleSize:
            self.fPatForRec.append(self.percentChange(self.avgLine[0], self.avgLine[i]))
            i += 1
        # print("fPatForRec", len(self.fPatForRec), self.fPatForRec)

    def howSimilar(self, source, target, sample):
        i = 0
        pastPat = []
        # print("source",source)
        # print("target", target)
        while i < sample:
            valor = 100.00 - self.percentChange(source[i], target[i])
            # valor = self.percentChange(source[i], target[i])
            # print("valor",valor)
            pastPat.append(valor)
            i += 1
        # if len(futuPat) > 0:
        # print("pastPat",pastPat)
        return reduce(lambda x, y: x + y, pastPat) / len(pastPat)
        # else:
        #    return 0

    def patternRecognition(self):
        ######
        predictedOutcomesAr = []
        ######
        plotPatAr = []
        patFound = 0
        global prevTrend
        global strength

        patForRec = self.patForRec
        fPatForRec = self.fPatForRec

        counter = 0
        currentPattern = self.patternAr[self.toWhat:]

        xp = []
        x = 1
        while x <= self.sampleSize:
            xp.append(x)
            x += 1

        # print("patForRec", len(patForRec))
        self.axes[0].cla()
        self.axes[0].plot(xp, patForRec, '#54fff7', linewidth=1)

        # print("currentPattern",len(currentPattern[0]))
        self.axes[1].cla()
        self.axes[1].plot(xp, self.avgLine[0:self.sampleSize], '#54fff7', linewidth=1)

        counter = self.toWhat
        # print("currentPattern",len(currentPattern))
        for eachPattern in currentPattern:
            # print("eachPattern",len(eachPattern))
            howSim = self.howSimilar(eachPattern, patForRec, self.sampleSize)
            # print("howSim",howSim)
            if howSim >= self.simPercent:
                patFound += 1
                plotPatAr.append(eachPattern)
                self.foundPartAr.append(eachPattern)
            else:
                self.notFoundPartAr.append(eachPattern)

        print("foundPartAr", len(self.foundPartAr), "notFoundPartAr", len(self.notFoundPartAr))

        print("patFound-->", patFound)
        predArray = []
        if patFound >= 5:
            # fig = plt.figure(figsize=(10,6))
            # plt.clf()

            for eachPatt in plotPatAr:
                # print("eachPatt",len(eachPatt))
                futurePoints = self.patternAr.index(eachPatt)
                #print("futurePoints", futurePoints)
                #print("self.performanceAr[futurePoints]", self.performanceAr[futurePoints],
                #      "patForRec[self.sampleSize-1]", patForRec[self.sampleSize - 1], "patForRec[0]", patForRec[0])
                #print(self.allData[self.toWhat - self.sampleSize], self.allData[self.toWhat],
                #      self.allData[self.toWhat + self.sampleSize], self.allData[futurePoints],
                #      self.allData[futurePoints + self.sampleSize])

                if self.performanceAr[futurePoints] > patForRec[self.sampleSize - 1]+0.1:
                    pcolor = '#24bc00'
                    #####
                    predArray.append(1.000)
                else:
                    pcolor = '#d40000'
                    #######
                    predArray.append(0)

                self.axes[0].plot(xp, eachPatt)

                predictedOutcomesAr.append(self.performanceAr[futurePoints])
                self.axes[0].scatter(35, self.performanceAr[futurePoints], c=pcolor, alpha=.4)

            reductedPredictedOutcomes = reduce(lambda x, y: x + y, predictedOutcomesAr) / len(predictedOutcomesAr)
            print("reductedPredictedOutcomes", reductedPredictedOutcomes)
            self.axes[0].scatter(38, reductedPredictedOutcomes, c=pcolor, alpha=.4)

            realOutcomeRange = self.allData[self.toWhat:self.toWhat + self.sampleSize]

            realDifference = abs(reductedPredictedOutcomes) + abs(patForRec[self.sampleSize - 1])

            realAvgOutcome = 0
            if len(realOutcomeRange) > 0:
                realAvgOutcome = reduce(lambda x, y: x + y, realOutcomeRange) / len(realOutcomeRange)

            # print('len(predictedOutcomesAr)-->',predictedOutcomesAr)
            predictedAvgOutcome = reduce(lambda x, y: x + y, predictedOutcomesAr) / len(predictedOutcomesAr)
            # print('predictedAvgOutcome:', predictedAvgOutcome)
            realMovement = self.percentChange(self.allData[self.toWhat], realAvgOutcome)
            print("realMovement", realMovement)
            self.axes[0].scatter(40, realMovement, c='#54fff7', s=25)

            # predictedPoint = self.fPatForRec[19]
            #
            # plt.scatter(45, predictedPoint, c='#54fff8', s=25)
            # actualPoint =self.patForRec[0]
            # plt.scatter(45, actualPoint, c='#54fff9', s=25)
            print("currentPrice-->", self.allData[self.toWhat])
            print("futurePrice-->", self.allData[self.toWhat + self.sampleSize])

            self.axes[0].plot(xp, patForRec, '#54fff7', linewidth=3)

            #######
            # print predArray
            if len(predArray) > 0:
                predictionAverage = reduce(lambda x, y: x + y, predArray) / len(predArray)
            else:
                predictionAverage = 0
            strength = len(predArray)
            print(predictionAverage, 'over', strength)

            # if predictionAverage < 0.00:
            #     print('drop predicted',patForRec[self.sampleSize-1],realMovement)
            #     if realMovement < reductedPredictedOutcomes:
            #         self.accuracyArray.append(100)
            #     else:
            #         self.accuracyArray.append(0)
            #
            # if predictionAverage > 0.00:
            #     print('rise predicted',patForRec[self.sampleSize-1],realMovement)
            #     if realMovement > reductedPredictedOutcomes:
            #         self.accuracyArray.append(100)
            #     else:
            #         self.accuracyArray.append(0)

            #######
            print('lprevTred', self.prevTrend)
            # if realDifference >= 1.0:
            # if predictionAverage > 0.00 and self.allData[self.toWhat + 20] > self.allData[self.toWhat] * (1.005):
            if predictionAverage > 0.5 and self.walletUSD > 0:
                print('SUBIDA')
                # if self.prevTrend == 'BAJADA':
                self.buyBTC(self.ask[self.toWhat])
            # if predictionAverage < 0.00 and self.allData[self.toWhat]>self.buyPrice*(1.0005):
            # print('BAJADA')
            # if self.prevTrend == 'SUBIDA':
            # self.sellBTC()

            if predictionAverage > 0.00:
                self.prevTrend = 'SUBIDA'
            if predictionAverage < 0.00:
                self.prevTrend = 'BAJADA'

            self.fig.tight_layout()
            plt.show()
            plt.pause(0.0001)

    def checkSellOrBuy(self):
        if self.walletBTC > 0.00 and self.bid[self.toWhat] > self.buyPrice * (1.005):
            self.sellBTC(self.bid[self.toWhat])

    def trainer(self):
        self.fig = plt.ion()
        # self.fig = plt.figure()

        self.fig, self.axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 5))

        dataLength = int(self.bid.shape[0])
        print('data length is', dataLength)
        #self.allData = ((self.bid+self.ask)/2)
        # self.allData = self.ask
        self.allData = self.ma20

        self.toWhat = self.sampleSize
        self.avgOriLine = self.allData
        self.avgLine = self.avgOriLine
        self.patternAr = []
        self.fPatternAr = []
        self.foundPartAr = []
        self.notFoundPartAr = []
        self.performanceAr = []

        TRADER.patternStorage()

        self.accuracyArray = []

        samps = 0
        accuracyAverage = 0
        self.toWhat = dataLength - 5000
        while self.toWhat < dataLength - 1:

            self.evaluate(self.toWhat)

            print('date:', self.date[self.toWhat], self.rawDate[self.toWhat])
            self.toWhat += 1
            samps += 1
            print('Entire processing took:', self.totalEnd, 'seconds')
            print('Backtested Accuracy is', str(accuracyAverage) + '% after', samps, 'actionable trades')
            print('bid:', self.bid[self.toWhat], 'ask:', self.ask[self.toWhat])
            print('WalletUSD:', self.walletUSD, 'WalletBTC:', self.walletBTC, "Current_value:",
                  self.allData[self.toWhat - 1], "buyPrice:", self.buyPrice, "sellPrice:", self.sellPrice)

    def evaluate(self, pointer):
        self.checkSellOrBuy()
        print("toWhat-->" + str(self.toWhat))
        self.avgLine = self.avgOriLine[self.toWhat - self.sampleSize:self.toWhat]
        # print("self.avgLine", self.avgLine)
        # print("self.avgLine",len(self.avgLine))
        self.patForRec = []
        self.fPatForRec = []
        self.currentPattern()
        self.patternRecognition()
        self.totalEnd = time.time() - self.totalStart
        if len(self.accuracyArray) > 0:
            accuracyAverage = reduce(lambda x, y: x + y, self.accuracyArray) / len(self.accuracyArray)

    def trader(self):
        self.seeding = False
        while True:
            print("-------------------------------")
            orders = self.polo.returnOpenOrders(currencyPair='USDT_BTC')
            print("orders:", orders)

            balance = self.polo.returnBalances()
            print("USDT:", balance['USDT'], "BTC:", balance['BTC'])
            self.walletBTC = float(balance['BTC'])
            self.walletUSD = float(balance['USDT'])

            self.orders = orders
            print("rawDate",self.rawDate[self.toWhat],"timestamp",int(datetime.datetime.utcnow().timestamp()))
            data = self.polo.returnChartData(self.lsymbol, self.lperiod, self.rawDate[self.toWhat],
                                             int(datetime.datetime.utcnow().timestamp()))
            for kline in data:
                print("kline-->", str(kline))
                print("kline-->", str(kline['date']), str(self.rawDate[self.toWhat]), "self.toWhat:", self.toWhat)
                if str(kline['date']) > str(self.rawDate[self.toWhat]):
                    append_to_file(self.filename, kline['date'], kline['open'], kline['close'],
                                        kline['weightedAverage'])
                    self.load_raw_record(kline['date'], kline['open'], kline['close'])
                    print("bid:", kline['open'], "ask:", kline['close'])
                    self.evaluate(self.toWhat)
                    self.toWhat += 1

            time.sleep(60)

    def load_raw_record(self, indate, inopen, inclose):
        self.rawDate = np.append(self.rawDate, float(indate))
        self.date = np.append(self.date, datetime.datetime.fromtimestamp(indate))
        self.ask = np.append(self.ask, float(inclose))
        self.bid = np.append(self.bid, float(inopen))
        #self.allData = np.append(self.allData,(inopen+inclose)/2)

        tempMA20 = (self.ask[self.toWhat - self.sampleSize:] / self.bid[
                                                               self.toWhat - self.sampleSize:]) / self.sampleSize
        self.allData = np.append(self.allData, tempMA20)
        self.avgOriLine = self.allData


if __name__ == "__main__":
    TRADER = Trader()

    #TRADER.openfile()

    TRADER.loadData()

    TRADER.trainer()

    TRADER.trader()
