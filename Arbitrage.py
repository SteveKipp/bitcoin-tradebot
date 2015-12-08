#python bot for trading between markets
#you need to run pip install requests first
#currently uses all public end points so no setup required for API usage
#TODO:
#   add fee data for each exchange
#   figure out transfer between wallets
#   switch buy/sell to ask/bid prices respectively
#   test :(


import sched, time, requests

#Define the URLs for each exchange
coinbase = 'https://api.exchange.coinbase.com/products/BTC-USD/book'
bitfinex = 'https://api.bitfinex.com/v1/pubticker/btcusd'
btc_e = 'https://btc-e.com/api/3/ticker/btc_usd'
OKCoin = 'https://www.okcoin.com/api/ticker.do?symbol=btc_usd&ok=1'
coinsetter = 'https://api.coinsetter.com/v1/marketdata/ticker'
bitstamp = 'https://www.bitstamp.net/api/ticker/'

#a class for holding all of the exchange data
class Exchange:
    'a common class for bitcoin exchanges'

    def __init__(self, name, dataURL, walletURL, apiKey, fee, tradeAccountBalance):
        self.name = name
        self.dataURL = dataURL
        self.walletURL = walletURL
        self.apiKey = apiKey
        self.fee = fee
        self.tradeAccountBalance = tradeAccountBalance
        self.bid = 0
        self.ask = 0



#initialize the exchanges
coinbase = Exchange('Coinbase',
                    'https://api.exchange.coinbase.com/products/BTC-USD/book',
                    0,
                    0, .0025, 100) #account created
bitfinex = Exchange('Bitfinex',
                    'https://api.bitfinex.com/v1/pubticker/btcusd',
                    0,
                    0, .0020, 100) #account created
btc_e = Exchange('BTC_E',
                 'https://btc-e.com/api/3/ticker/btc_usd',
                 0,
                 0, .0020, 100) #missing account
OKCoin = Exchange('OKCoin',
                  'https://www.okcoin.com/api/ticker.do?symbol=btc_usd&ok=1',
                  0,
                  0, .0020, 100) #missing account
bitstamp = Exchange('Bitstamp',
                    'https://www.bitstamp.net/api/ticker/',
                    0,
                    0, .0025, 100) #missing account


def getCurrentData():

    #python scoping, not even once
    #global coinbase
    #global bitfinex
    #global btc_e
    #global OKCoin
    #global bitstamp

    coinbase.bid = requests.get(coinbase.dataURL).json()['bids'][0][0]
    bitfinex.bid = requests.get(bitfinex.dataURL).json()['bid']
    btc_e.bid = requests.get(btc_e.dataURL).json()['btc_usd']['buy']
    OKCoin.bid = requests.get(OKCoin.dataURL).json()['ticker']['buy']
    #cs = requests.get(coinsetter)
    bitstamp.bid = requests.get(bitstamp.dataURL).json()['bid']

    #this will be really shitty latency but I'm doing it for test purposes
    coinbase.ask = requests.get(coinbase.dataURL).json()['asks'][0][0]
    bitfinex.ask = requests.get(bitfinex.dataURL).json()['ask']
    btc_e.ask = requests.get(btc_e.dataURL).json()['btc_usd']['sell']
    OKCoin.ask = requests.get(OKCoin.dataURL).json()['ticker']['sell']
    #cs = requests.get(coinsetter)
    bitstamp.ask = requests.get(bitstamp.dataURL).json()['ask']



    print "Coinbase -> bid: "+coinbase.bid+" ask: "+coinbase.ask
    print "Bitfinex -> bid: "+bitfinex.bid+" ask: "+bitfinex.ask
    print "BTC_E -> bid: "+str(btc_e.bid)+" ask: "+str(btc_e.ask)
    print "OKCoin -> bid: "+OKCoin.bid+" ask: "+OKCoin.ask
    #Coinsetter was getting strangely precise returns like 365.0 367.0 etc...
    #print "Coinsetter: "+str(cs.json()['bid']['price'])
    print "Bitstamp -> bid: "+bitstamp.bid+" ask: "+bitstamp.ask
    print '\n'

    exchanges = [coinbase, bitfinex, btc_e, OKCoin, bitstamp]

    return exchanges

s = sched.scheduler(time.time, time.sleep)

#globals
highestToDate = 0
buySellFlag = 'B'

#Starting Values:
# US Dollars - 10
# bitcoin - 0
# hence buying on the first iteration
USD = 10
BTC = 0

def tick(sc):
    global buySellFlag
    global USD
    global BTC

    print("%%%%%%%%%% NEW TICK %%%%%%%%%%")
    data = getCurrentData()

    #core alternation
    if buySellFlag == 'B':
        calculateBuyDifference(data)
        buySellFlag = 'S'
    elif buySellFlag == 'S':
        calculateSellDifference(data)
        buySellFlag = 'B'
    else:
        print 'buy or sell flag has some how escaped buying or selling, not good'

    #Current Stats Output
    print 'Portfolio -> USD: '+str(USD)+'\t BTC: '+str(BTC)+'\n'

    # 60 seconds per tick
    sc.enter(60, 1, tick, (sc,))


def calculateBuyDifference(exchangeData):
    exchangeData = sorted(exchangeData, key=lambda exchange: exchange.bid)
    lowest = exchangeData[0]
    global USD
    global BTC

    BTCPreFee = USD/float(lowest.bid)
    BTC = BTCPreFee - (BTCPreFee * lowest.fee)
    USD = 0
    print 'BUY: '+str(BTC)+' @ $'+str(lowest.bid)+' on '+lowest.name+'\n'

def calculateSellDifference(exchangeData):
    exchangeData = sorted(exchangeData, key=lambda exchange: exchange.ask)
    highest = exchangeData[len(exchangeData)-1]
    global USD
    global BTC
    USDPreFee = float(highest.ask) * BTC
    USD = USDPreFee - (USDPreFee * highest.fee)
    print 'SELL: '+str(BTC)+' @ $'+str(highest.ask)+' on '+highest.name+'\n'
    BTC = 0

def getTotalPortfolio(exchangeData):
    #TODO: aggregate across all of the trade accounts
    return 'butts'

s.enter(60, 1, tick, (s,))
s.run()
