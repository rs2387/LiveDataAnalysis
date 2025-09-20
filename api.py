#importing modules / libraries
from binance.client import Client
from datetime import datetime

#initialises the binance client
client = Client()

#define a function to get candles of a custom timeframe with the user's given parameters
def getCustomCandles(symbol: str ,interval: str, intervalSeperation=1,  totalCandles=15):
    
    #checks how many candles are needed because e.g. for a 5 second candle you need to combine 5 1-second candles
    requiredIntervalCandles = totalCandles * intervalSeperation 
    klines = client.get_klines(symbol=symbol, interval=interval, limit=requiredIntervalCandles)

    #if the API does not return enough values then I raise an import error
    if not klines or len(klines) < requiredIntervalCandles:
        raise ImportError 

    #converts raw klines to my wanted format of a list with time, open, high, low, close
    candleData = []
    for k in klines: #loop through each candle and append a list of data for each
        candleData.append([datetime.fromtimestamp(int(k[0]) / 1000),
                   float(k[1]), float(k[2]), float(k[3]), float(k[4])])

    #combine into my user's desired interval e.g. 5s, 15s, 5m, 15m
    combinedCandles = []
    for i in range(0, len(candleData), intervalSeperation):
        manyCandles = candleData[i:i + intervalSeperation]

        #skip if the number of candles in the chunk is not the wanted interval
        if len(manyCandles) < intervalSeperation:
            break

        #combined candle uses first timestamp, first open, last close, highest high and lowest low
        timestamp = manyCandles[0][0]
        openPrice = manyCandles[0][1]
        closePrice = manyCandles[-1][4]
        highPrice = max(high[2] for high in manyCandles)
        lowPrice = min(low[3] for low in manyCandles)

        #add the new combined candle to the list
        combinedCandles.append([timestamp, openPrice, highPrice, lowPrice, closePrice])

    return combinedCandles #return the whoel list of combined candles




#function definition to calulate rsi, parameters are a list of closing prices
#and default period for Relative Strength Index
def calculateRSI(prices:list, period=14):

        #two empty lists for gains and losses
        gains, losses = [], []
        
        #loops through input list and appends the absoulte difference between
        #the two most recent closing prices to its respective list
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i - 1]
            gains.append(max(diff, 0))
            losses.append(abs(min(diff, 0)))

        #figures out how the total gain within the last 14 periods
        #finds an average by dividing the total by number of gains
        totalGain = 0
        for i in range(len(gains[:period])):
            totalGain += gains[:period][i]
        avgGain = totalGain / len(gains[:period])

        #figures out how the total loss within the last 14 periods
        #finds an average by dividing the total by number of losses
        totalLoss = 0
        for i in range(len(losses[:period])):
            totalLoss += losses[:period][i]
        avgLoss = totalLoss / len(losses[:period])

        #initialises empty list for rsi values
        rsiValues = []
        #loops through each closing price in the input list, and calculate rsi
        for i in range(period, len(prices)):
            #smooths the average gain and loss for each period
            avgGain = (avgGain * (period - 1) + gains[i - 1]) / period
            avgLoss = (avgLoss * (period - 1) + losses[i - 1]) / period
            #relative strength is ratio between average gain and loss
            rs = avgGain / avgLoss if avgLoss != 0 else 100
            #relative strength index scales the rs between 0 and 100
            rsi = 100 - (100 / (1 + rs))
            rsiValues.append(rsi)

        return rsiValues


#function definition to calculate Expontial Moving Average
def ema(data, period, sma=True):

    #calculates the smoothing factor for the ema, which decides the weight given to previous values
    alpha = 2 / (period + 1)

    #initialises ema values list with a simple moving average as first term
    #the standard ema calulation starts the recursion using the sma
    #(simple moving average) of the first 14 data points
    #this is more effective but given 30 closing prices, only 16 ema values
    #will be calculated and with limited data points from the API
    if sma:
        emaValues = [sum(data[:period]) / period]
        #recursive function that takes the most recent ema value and feeds it
        #back through into the equation
        for price in data[period:]:
            emaValues.append((price - emaValues[-1]) * alpha + emaValues[-1])
    #I had to use an alternative method taking the first data point as the
    #initial ema value when required instead of calculating an sma
    else:
        #recursive function that takes the most recent ema value and feeds it
        #back through into the equation
        emaValues = [data[0]]
        for i in range(1, len(data)):
            emaValues.append((data[i] - emaValues[-1]) * alpha + emaValues[-1])



    return emaValues

#function definition to calculate Average Directional Index
def calculateADX(highs, lows, closes, period=14):

    #initialise lists for true range, positiveDirectionalMovement, and negativeDirectionalMovement
    trueRange,positiveDirectionalMovement, negativeDirectionalMovement = [], [], []

    #this loops through all the prices and assigns values to the following:
    for i in range(1, len(highs)):
        currentHigh = highs[i]
        currentLow = lows[i]
        previousClose = closes[i - 1]
        previousHigh = highs[i - 1]
        previousLow = lows[i - 1]

        #true range is calculated and appended. true range is a measure of volatility
        trueRange.append(max(currentHigh - currentLow, abs(currentHigh - previousClose), abs(currentLow - previousClose)))

        #calculates positiveDirectionalMovement and negativeDirectionalMovement
        #directional movement is positive if the current high is greater than the previous high and the difference 
        #between them is greater than the difference between the previous low and the current low
        if currentHigh - previousHigh > previousLow - currentLow and currentHigh - previousHigh > 0:
            positiveDirectionalMovement.append(currentHigh - previousHigh)
        else:
            positiveDirectionalMovement.append(0)
        #directional movement is negative if the previous low is greater than the current low, and if difference
        #between then is greater than the difference between current high and the previous high
        if previousLow - currentLow > currentHigh - previousHigh and previousLow - currentLow > 0:
            negativeDirectionalMovement.append(previousLow - currentLow)
        else:
            negativeDirectionalMovement.append(0)


    #smooth the true range, positiveDirectionalMovement, and negativeDirectionalMovement
    #over 14 periods using the ema function from previously
    smoothedTrueRange = ema(trueRange, period)
    smoothedPositiveDirectionalMovement = ema(positiveDirectionalMovement, period)
    smoothedNegativeDirectionalMovement = ema(negativeDirectionalMovement, period)

    #initialise empty lists for positiveDirectionalIndex, negativeDirectionalIndex and directionalIndex
    positiveDirectionalIndex, negativeDirectionalIndex, directionalIndex= [], [], []

    #calculate positiveDirectionalIndex and negativeDirectionalIndex
    #go through the smoothed positiveDirectionalMovement, negativeDirectionalMovement and the smoothed tr values
    for i in range(len(smoothedTrueRange)):
        #check for zero division to prevent any future errors
        if smoothedTrueRange[i] != 0:
            positiveDirectionalIndex.append((smoothedPositiveDirectionalMovement[i] / smoothedTrueRange[i]) * 100)
            negativeDirectionalIndex.append((smoothedNegativeDirectionalMovement[i] / smoothedTrueRange[i]) * 100)
        #if the true range is 0, the directional indicators are both 0
        else:
            positiveDirectionalIndex.append(0)
            negativeDirectionalIndex.append(0)


    #go through positiveDirectionalIndex and negativeDirectionalIndex values
    for i in range(len(positiveDirectionalIndex)):
        #again checking for zero division
        if positiveDirectionalIndex[i] + negativeDirectionalIndex[i] != 0:
            #directionalIndex is the strength of the trend and calculate with this formula
            directionalIndex.append(abs(positiveDirectionalIndex[i] - negativeDirectionalIndex[i]) / (positiveDirectionalIndex[i] + negativeDirectionalIndex[i]) * 100)
        #if both indicators are 0, directionalIndex is also 0
        else:
            directionalIndex.append(0)

    #smoothed average of directionalIndex over 14 periods calling ema function
    #I set sma= True in the ema earlier
    #to make it more accurate I should be doing it with another 14 period but due to
    #data limitations with the API, I unfortunately cannot, so I settled with 12
    adx = ema(directionalIndex, 12, sma=True)

    return adx



#function definition to calculate  Moving Average Convergence Divergence
#useful for identifying buy and sell signals and spotting momentum
def calculateMACD(close, fastPeriod=12, slowPeriod=26, signalPeriod=9, negate=True):

    #calculate ema for fast period and slow period
    fastEma = ema(close, fastPeriod)
    slowEma = ema(close, slowPeriod)

    #initialise empty list for macd values and histogram
    macdValues, histogram = [], []

    for i in range(len(slowEma)):
        #the macd is the difference between fast and slow ema
        macdValue = fastEma[i] - slowEma[i]
        #divergence is represented more clearly when the graph is flipped so I negate it
        if negate:
            macdValue = -macdValue
        macdValues.append(macdValue)


    #signal line smooths out macd values to try identify crossovers
    #sma is False unlike before because it would require a lot more data points
    signalLine = ema(macdValues, signalPeriod, sma=False)


    #the histogram will help my user to visualise momentum
    #subtracts signal line from macd values
    for i in range(len(macdValues)):
        histogram.append(macdValues[i] - signalLine[i])

    return macdValues, signalLine, histogram
