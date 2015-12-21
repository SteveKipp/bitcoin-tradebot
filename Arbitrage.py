#python bot for trading between markets
#you need to run pip install requests first
#currently uses all public end points so no setup required for API usage
#TODO:
#   add fee data for each exchange
#   figure out transfer between wallets
#   switch buy/sell to ask/bid prices respectively
#   test :(


import sched, time, requests, sys

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

    def __init__(self, name, dataURL, walletURL, apiKey, fee, tradeAccountUSD):
        self.name = name
        self.dataURL = dataURL
        self.walletURL = walletURL
        self.apiKey = apiKey
        self.fee = fee
        self.tradeAccountUSD = tradeAccountUSD
        self.tradeAccountBTC = 0
        self.bid = 0
        self.ask = 0



#initialize the exchanges
coinbase = Exchange('Coinbase',
                    'https://api.exchange.coinbase.com/products/BTC-USD/book',
                    0,
                    0, .0025, 300) #account created
bitfinex = Exchange('Bitfinex',
                    'https://api.bitfinex.com/v1/pubticker/btcusd',
                    0,
                    0, .0020, 300) #account created
btc_e = Exchange('BTC_E',
                 'https://btc-e.com/api/3/ticker/btc_usd',
                 0,
                 0, .0020, 300) #missing account
OKCoin = Exchange('OKCoin',
                  'https://www.okcoin.com/api/ticker.do?symbol=btc_usd&ok=1',
                  0,
                  0, .0020, 300) #missing account
bitstamp = Exchange('Bitstamp',
                    'https://www.bitstamp.net/api/ticker/',
                    0,
                    0, .0025, 300) #missing account


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
exchangeData = getCurrentData()

#Starting Values:
# US Dollars - 10
# bitcoin - 0
# hence buying on the first iteration
totalUSD = 10
BTC = 0

def tick(sc):
    global buySellFlag
    global USD
    global BTC
    global exchangeData

    print("%%%%%%%%%% NEW TICK %%%%%%%%%%")
    exchangeData = getCurrentData()

    #core alternation
    if buySellFlag == 'B':
        calculateBuyDifference()
        buySellFlag = 'S'
    elif buySellFlag == 'S':
        calculateSellDifference()
        buySellFlag = 'B'
    else:
        print 'buy or sell flag has some how escaped buying or selling, not good'

    #Current Stats Output
    print 'Portfolio -> USD: '+str(getTotalUSD())+'\t BTC: '+str(getTotalBTC())+'\n'

    # 60 seconds per tick (1 minute for testing purposes)
    sc.enter(60, 1, tick, (sc,))

def getTotalUSD():
    global exchangeData
    USD = 0
    for exchange in exchangeData:
        USD += exchange.tradeAccountUSD

    return USD

def getTotalBTC():
    global exchangeData
    totalBTC = 0
    for exchange in exchangeData:
        totalBTC += exchange.tradeAccountBTC

    return totalBTC


def calculateBuyDifference():
    global exchangeData
    global totalUSD
    lowest = sorted(exchangeData, key=lambda exchange: exchange.bid)[0]
    if lowest.tradeAccountUSD < totalUSD:
        print 'Cant buy on '+lowest.name+ ' USD in trade account too low ('+str(lowest.tradeAccountUSD)+')'
        sys.exit()

    #This is causing some sort of rounding error
    # the strange consistency of 1490.0  on buy for a very long time
    BTCPreFee = totalUSD/float(lowest.bid)

    sorted(exchangeData, key=lambda exchange: exchange.bid)[0].tradeAccountBTC += BTCPreFee - (BTCPreFee * lowest.fee)
    sorted(exchangeData, key=lambda exchange: exchange.bid)[0].tradeAccountUSD -= totalUSD

    #update array

    print 'BUY: '+str(lowest.tradeAccountBTC)+' @ $'+str(lowest.bid)+' on '+lowest.name+'\n'


#note to self: going to have to define a move function that moves the bitcoin
#               from the buy exchange to the sell exchange
#               moveBTC(exchangeData):
def moveBTC(from1, to):
    global exchangeData
    for x in range(0,len(exchangeData)):
        if exchangeData[x].name == from1.name:
            ex1 = x
        if exchangeData[x].name == to.name:
            ex2 = x
    exchangeData[ex2].tradeAccountBTC = exchangeData[ex1].tradeAccountBTC
    print 'Moved '+str(from1.tradeAccountBTC)+ " BTC from "+from1.name+" to "+to.name
    exchangeData[ex1].tradeAccountBTC = 0

def calculateSellDifference():
    global exchangeData
    global totalUSD
    highest = sorted(exchangeData, key=lambda exchange: exchange.ask)[len(exchangeData)-1]
    BTCLocation = sorted(exchangeData, key=lambda exchange: exchange.tradeAccountBTC)[len(exchangeData)-1]
    moveBTC(BTCLocation, highest)
    USDPreFee = float(highest.ask) * highest.tradeAccountBTC
    sorted(exchangeData, key=lambda exchange: exchange.ask)[len(exchangeData)-1].tradeAccountUSD += USDPreFee - (USDPreFee * highest.fee)
    totalUSD = USDPreFee - (USDPreFee * highest.fee)
    print 'SELL: '+str(highest.tradeAccountBTC)+' @ $'+str(highest.ask)+' on '+highest.name+'\n'
    sorted(exchangeData, key=lambda exchange: exchange.ask)[len(exchangeData)-1].tradeAccountBTC = 0

def getTotalPortfolio(exchangeData):
    #TODO: aggregate across all of the trade accounts
    return 'butts'

s.enter(60, 1, tick, (s,))
s.run()
