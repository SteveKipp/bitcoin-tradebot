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

    def __init__(self, name, dataURL, walletURL, apiKey, fee):
        self.name = name
        self.dataURL = dataURL
        self.walletURL = walletURL
        self.apiKey = apiKey
        self.fee = fee
        self.price = 0



#initialize the exchanges
coinbase = Exchange('Coinbase',
                    'https://api.exchange.coinbase.com/products/BTC-USD/book',
                    0,
                    0, .0025) #account created
bitfinex = Exchange('Bitfinex',
                    'https://api.bitfinex.com/v1/pubticker/btcusd',
                    0,
                    0, .0020) #account created
btc_e = Exchange('BTC_E',
                 'https://btc-e.com/api/3/ticker/btc_usd',
                 0,
                 0, .0020) #missing account
OKCoin = Exchange('OKCoin',
                  'https://www.okcoin.com/api/ticker.do?symbol=btc_usd&ok=1',
                  0,
                  0, .0020) #missing account
bitstamp = Exchange('Bitstamp',
                    'https://www.bitstamp.net/api/ticker/',
                    0,
                    0, .0025) #missing account


def getCurrentData():

    #python scoping, not even once
    #global coinbase
    #global bitfinex
    #global btc_e
    #global OKCoin
    #global bitstamp

    coinbase.price = requests.get(coinbase.dataURL).json()['bids'][0][0]
    bitfinex.price = requests.get(bitfinex.dataURL).json()['bid']
    btc_e.price = requests.get(btc_e.dataURL).json()['btc_usd']['buy']
    OKCoin.price = requests.get(OKCoin.dataURL).json()['ticker']['buy']
    #cs = requests.get(coinsetter)
    bitstamp.price = requests.get(bitstamp.dataURL).json()['bid']

    print "Coinbase: "+coinbase.price
    print "Bitfinex: "+bitfinex.price
    print "BTC_E: "+str(btc_e.price)
    print "OKCoin: "+OKCoin.price
    #Coinsetter was getting strangely precise returns like 365.0 367.0 etc...
    #print "Coinsetter: "+str(cs.json()['bid']['price'])
    print "Bitstamp: "+bitstamp.price
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
    exchangeData = sorted(exchangeData, key=lambda exchange: exchange.price)
    lowest = exchangeData[0]
    global USD
    global BTC

    BTCPreFee = USD/float(lowest.price)
    BTC = BTCPreFee - (BTCPreFee * lowest.fee)
    USD = 0
    print 'BUY: '+str(BTC)+' @ $'+str(lowest.price)+' on '+lowest.name+'\n'

def calculateSellDifference(exchangeData):
    exchangeData = sorted(exchangeData, key=lambda exchange: exchange.price)
    highest = exchangeData[len(exchangeData)-1]
    global USD
    global BTC
    USDPreFee = float(highest.price) * BTC
    USD = USDPreFee - (USDPreFee * highest.fee)
    print 'SELL: '+str(BTC)+' @ $'+str(highest.price)+' on '+highest.name+'\n'
    BTC = 0

s.enter(60, 1, tick, (s,))
s.run()
