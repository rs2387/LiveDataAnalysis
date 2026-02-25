#importing modules / libraries
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime
import json
import websocket
import threading
#importing functions from my other files
from database import addCrypto
from api import getCustomCandles, calculateRSI, calculateADX, calculateMACD

#this flag is used to close the websocket safely when a user closes the window
flag = True

#creates a class for my candles app
class CandlesApp(tk.Tk):
    #initiliasing constructor takes parameters based on user inputs for versatility
    def __init__(self, interval: str, ticker: str, socketNeeded:bool):

        #since this class is going to be called within another class, it makes sure that the
        #parent class is initialised properly
        super().__init__()

        
        self.title("Candlestick chart") #sets the title of the app
        self.geometry("1000x650") #sets the size of the app 1000 in x and 650 in y
        #calls the on_quit function to terminate the program safely if the window is closed by the user
        self.protocol("WM_DELETE_WINDOW", self.onUserQuit)

        
        self.tempStorage = [] #temporary storage place to be used later for combining candles
        self.period = interval[-1] #e.g. for interval of 30m, period = m 
        #makes default value 1, only changes for custom intervals where I need to combine candles
        self.intervalSeperation = 1 
        self.ticker = ticker #makes the ticker accessible for me across the the whole program

        #depending on whether the websocket will be running or not, functions will need to be handled
        #differently, so I need to make the boolean value accessible everywhere in the program
        self.socket = socketNeeded

        #the websocket is only needed for second or minute time frames and can only collect data every minute
        #or second so if the interval is a scalar of that like "5m", I need to change the interval
        #seperation to 5 or whatever else it may be
        if self.socket == True:
            self.interval = self.socketInterval = "1s" if self.period == "s" else "1m"
            if interval != self.interval:
                self.intervalSeperation = int(interval[:-1])
        else: #if a websocket is not needed, the interval remains the same
            self.interval = interval
        
        #initialise the lists for timestamps, open, high, low and close prices
        self.timeData, self.openData, self.highData, self.lowData, self.closeData = [], [], [], [], []

        #prevents multiple threads from accessing a shared resource at the same time
        self.lock = threading.Lock()

        #calls the next method to create the frame for my candlestick graph
        self.openFrame()

    #this method creates and opens the frame to put the candlestick graph on
    def openFrame(self):
        
        #creates a frame attribute for self
        self.frame = tk.Frame(self)
        #places the frame inside its parent widget and can expand in both x and y directions
        self.frame.pack(fill=tk.BOTH, expand=True)
        #creates a figure and axis attributes for self with 4 subplots
        #each subplot will be used to display seperate items e.g. candlestick, RSI, ADX, MACD
        #gridspec creates a height ratio to make the candlestick graph longer than the ADX and RSI and MACD ones
        self.figure, self.axs = plt.subplots(4, figsize=(8, 8), sharex= True, gridspec_kw={'height_ratios': [3, 1, 1, 1]})

        #sets the title of this window
        self.axs[0].set_title(f"{self.ticker} Candlestick chart")
        self.figure.patch.set_facecolor("#2C2C2C") #sets the frame colour
        #loops through each subplot and sets their face colour
        for i in range(0,4):
            self.axs[i].set_facecolor('#404040')
        
        #creates a canvas attribute that places the figure into the frame and allows expansion in x and y directions
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        #calls a method to get the initial candles using the Binance API
        self.getInitialCandles()
    
        #if the users selection needs a websocket, I need to open it in a seperate thread to not interrupt the tkinter window
        if self.socket:
            #creates a thread where the websocket stream method is called to return live data
            self.websocketThread = threading.Thread(target=self.websocketStream, args=(self.ticker, self.socketInterval))
            self.websocketThread.start() #starts the thread

    #this method just fetches all the initial candles to be plotted
    def getInitialCandles(self):

        #if a websocket is needed, I want to display less initial candles since it will be updated with live data
        if self.socket:
            self.totalCandles = 65
            #calls a function to connect to binance API and returns combined candles for my user's given interval and cryptocurrency
            self.candles = getCustomCandles(f"{self.ticker}", self.interval, self.intervalSeperation, totalCandles=self.totalCandles)
        else:
            self.totalCandles = 85
            #calls a function to connect to binance API and returns combined candles for my user's given interval and cryptocurrency
            self.candles = getCustomCandles(f"{self.ticker}", self.interval, totalCandles=self.totalCandles)

        #out of the total candles, take 85 as an example, only the last 60 will be plotted as candlesticks
        #the first 26 extra (0-25 inclusive) are needed for the macd calculations, and the rsi and adx values will be
        #11-25 inclusive, so the first 26 candles will not be plotted, just used for calculations

        #loop through each candle to pass all of the data another method 
        for candle in self.candles:
            timeStamp, openPrice, highPrice, lowPrice, closePrice = candle
            #the False means that it is the initial data being added, and the method allows me to organise
            #all the data im handling within the app a lot better
            self.addCandlestickData(timeStamp, openPrice, highPrice, lowPrice, closePrice, False) 

    #this method is used to add data to controlled lists to keep everything organised
    def addCandlestickData(self, timeStamp, openPrice, highPrice, lowPrice, closePrice, extra=True):

        #keeps the list size under control, so that the graph doesn't get too squished with too many data points
        if len(self.timeData) > self.totalCandles:
            #removes the first / oldest candle from the list
            self.timeData.pop(0), self.openData.pop(0), self.highData.pop(0)
            self.closeData.pop(0), self.lowData.pop(0)

        #appends each new data value to its respective list
        self.timeData.append(timeStamp), self.openData.append(openPrice),self.highData.append(highPrice)
        self.lowData.append(lowPrice), self.closeData.append(closePrice)

        #if the program is only plotting initial candles, then I can call plot candlesticks simply
        if not extra and len(self.timeData)>25: #have to wait until I have enough values to plot MACD
            self.plotCandlesticks()
        #if the program is plotting live data on top of the old data, I have to manually call the function
        #after a given time (0 seconds), otherwise it will cause an obstruction
        elif len(self.timeData)>25:
            self.after(0, self.plotCandlesticks)

    #this method will connect me to a websocket and append live data values to the lists
    def websocketStream(self, ticker: str, interval: str):

        #assigns the user's chosen ticker to part of the "url" 
        asset = ticker.lower() + f"@kline_{interval}"
        
        #defining a function for when the message is first recieved
        def onMessage(ws, message: list):
            #try except statement for error handling in case the data message is not recieved properly
            try:
                #load the message as a json dictionary and use keys to get the specific values
                message = (json.loads(message))["data"]["k"]

                #if statement makes sure that the close price is final
                if message["x"]:
                    #assigns all values to designated variables to be appended into list
                    openPrice = float(message["o"])
                    closePrice = float(message["c"])
                    highPrice = float(message["h"])
                    lowPrice = float(message["l"])
                    #converts milliseconds into a datetime object
                    timeStamp = datetime.fromtimestamp(int(message["t"]) / 1000)
                    #combine and process the candle data
                    self.combineCandles(timeStamp, openPrice, highPrice, lowPrice, closePrice)

            #if an error occurs it will print it out in an easy to pinpoint way
            except Exception as e:
                print(f"Error processing message : {e}")

        #prints in the terminal when the websocket connection open to ensure everything is working
        def onOpen(ws): #define a function for when the websocket opens
            print("WebSocket connection opened : ")

        #define a function for when the websocket is closed
        def onClose(ws, closeStatusCode=None, closeMsg=None):
            if closeStatusCode:
                #prints the status code if there is one
                print(f"WebSocket closed with status code : {closeStatusCode}")
                self.quit() #quits the program
            elif closeMsg:
                print(f"WebSocket closed : {closeMsg}")
                #resets the global flag in case this class is called more than once in one running
                global flag
                flag = True
                #destroy the frame then everything else
                self.frame.destroy()
                self.destroy()
            else:
                #otherwise just close the websocket normally
                print("WebSocket closed. ")
                self.quit()

        #the websocket stream url that the library connects to
        socket = "wss://stream.binance.com:9443/stream?streams=" + asset
        ws = websocket.WebSocket()
        ws.connect(socket)
        onOpen(ws) #calls the on open function

        #an infinte while loop only broken when the flag is false which is when the user closes the window
        #or if the websocket is closed due to maintenance, or if there is an error
        while True:
            if flag:
                #try to recieve the message and if not quit the program and
                try:
                    message = ws.recv()
                    if message:
                        onMessage(ws, message)
                    else:
                        #if the message has no data but didnt raise an error
                        ws.close()
                        onClose(ws, closeMsg="Message recieved empty")
                        break
                #if the message raised an error or exception
                except Exception as e:
                    ws.close()
                    onClose(ws, closeMsg="Error recieing message")
                    break
            #if the user has closed the tab, the close function is called and the program terminates
            elif flag == False:
                ws.close()
                onClose(ws, None, "User closed tab. ")
                self.quit()
                break
    #method to combine the candlestick data if needed
    def combineCandles(self, timeStamp, openPrice, highPrice, lowPrice, closePrice):
        #execute this function while keeping it locked to a single thread
        with self.lock:
            
            #append the data into a temporary storage place
            self.tempStorage.append([timeStamp, openPrice, highPrice, lowPrice, closePrice])

            #when the desired interval is reached, there will be that many candles in the temp storage
            if len(self.tempStorage) >= self.intervalSeperation:
                #the combined candle will have the first timestamp, the last close, the first open
                #the highest high and the lowest low
                openPrice = self.tempStorage[0][1]
                closePrice = self.tempStorage[-1][4]
                highPrice = max(candle[2] for candle in self.tempStorage)
                lowPrice = min(candle[3] for candle in self.tempStorage)
                timeStamp = self.tempStorage[0][0]

                #clears the temporary storage for the next set of combined candles
                self.tempStorage = self.tempStorage[self.intervalSeperation:]
    
                #uses the new values as parameters for the adding candlestick data method
                self.addCandlestickData(timeStamp, openPrice, highPrice, lowPrice, closePrice)


    #this method plots each candlestick onto the graph and subplots
    def plotCandlesticks(self):

        #a lot happens at once in this function at a fast pace so if something goes wrong, I want to be notified
        #but hopefully it will carry on working soon after
        try:
            #use iteration to clear each subplot
            labels = ["Price", "MACD", "RSI", "ADX"]
            for i in range(0,4): #loop through each subplot and manage aesthetics
                self.axs[i].clear()
                self.axs[i].tick_params(axis='both', colors='white')
                self.axs[i].set_ylabel(labels[i], color="white")

            #a dictionary of formats, where self.period acts as key to get certain timestamp values for the x axis formatter
            formats = {"s": '%H:%M:%S', "m": '%H:%M:%S', "h": '%m-%d-%H', "d": '%Y-%m-%d', "w": '%Y-%m-%d', "M": '%Y-%m-%d'}
            self.axs[0].xaxis.set_major_formatter(mdates.DateFormatter(f'{formats[self.period]}'))

            #sets a limit on the x axis to be between fist and last timestamps of the candlesticks plotted
            #this means that whenever an old candle is popped and a new one is drawn, it will appear to be sliding
            if len(self.timeData)>23:
                #the left limit is just the time stamp of the unplotted candle before the first plotted candle
                #the right limit is more complex, it calculates the time difference between the last two candles and
                #adds it on to the the final timestamp to push the limit forward by what would have been one candle
                #it also required me to change types several times (datetime to number back to datetime)
                upperLimit = mdates.num2date(mdates.date2num(self.timeData[-1]) * 2 - mdates.date2num(self.timeData[-2]))
                self.axs[0].set_xlim(left=self.timeData[24], right = upperLimit)

            #if the websocket is running, the x axis grid lines intervals are either in seconds or minutes 
            if self.socket:
                #set the x axis label to Time in white 
                self.axs[0].set_xlabel("Time", color="white")
                #if the period is seconds, a second locator will place interval every 10 candles
                if self.period == "s":
                    self.axs[0].xaxis.set_major_locator(mdates.SecondLocator(interval=self.intervalSeperation*10)) 
                else: #otherwise its in minutes
                    self.axs[0].xaxis.set_major_locator(mdates.MinuteLocator(interval=self.intervalSeperation*10))
            else:
                #most of these periods use date as their x axis with colour white
                self.axs[0].set_xlabel("Date", color="white")
                #all different periods have different statements to give more even intervals for each graph
                #the long selection statement is exhaustive but necessary
                if self.period == "m":
                    self.axs[0].set_xlabel("Time", color="white")
                    self.axs[0].xaxis.set_major_locator(mdates.HourLocator(interval=2))
                elif self.interval == "1h" or self.interval == "4h":
                    self.axs[0].set_xlabel("Month-Day-Hour", color="white")
                    self.axs[0].xaxis.set_major_locator(mdates.HourLocator(interval=16))
                elif self.interval == "6h" or self.interval == "8h" or self.interval == "12h":
                    self.axs[0].xaxis.set_major_locator(mdates.DayLocator(interval=4))
                elif self.period == "d":
                    self.axs[0].xaxis.set_major_locator(mdates.DayLocator(interval=12))
                elif self.period == "w":
                    self.axs[0].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                elif self.period == "M":
                    self.axs[0].xaxis.set_major_locator(mdates.MonthLocator(interval=12)) 
            
            #sets a grid on the candlestick graph at each major locator with a light grey colour and 0.5 opacity
            self.axs[0].grid(True, color='#666666', alpha=0.5)

            #sets a range for the y axis between 0 and 100 - typical for RSI 
            self.axs[2].set_ylim(0,100)
            #sets dashed lines at 70 and 30 because RSI's position relative to these is the most important
            self.axs[2].axhline(70, linestyle="dashed", color="#FF0000")
            self.axs[2].axhline(30, linestyle="dashed", color="#00FF00")

            #sets a range for the y axis between 0 and 100 - typical for ADX
            self.axs[3].set_ylim(0,100)
            self.axs[3].axhline(25, linestyle="dashed", color="#D3D3D3") 

            #calls a function to calculate rsi e.g. given the last 74 values so will return the rsi of the last 60
            rsi = calculateRSI(self.closeData[11:])
            #calls a function to calculate adx e.g. given the last 85 values so will return the adx of the last 60
            adx = calculateADX(self.highData, self.lowData,self.closeData)
            #valid values for these start at the 26th data point. If 85 values passed in, 60 are returned 
            macd, signalLine, histogram = calculateMACD(self.closeData)
            
            #plots each candlestick with the corresponfing indicator values starting at 26th
            for i in range(len(self.timeData[25:])):
                #colour is green if the close price is greater than the open price, otherwise red
                color = '#00EE00' if self.closeData[25:][i] > self.openData[25:][i] else '#E63946'
                #plots the high to low line with a smaller width
                self.axs[0].plot([self.timeData[25:][i], self.timeData[25:][i]], [self.lowData[25:][i], self.highData[25:][i]], color=color, lw=1) 
                #plots the candle body (between open and close) with a bigger width
                self.axs[0].plot([self.timeData[25:][i], self.timeData[25:][i]], [self.openData[25:][i], self.closeData[25:][i]], color=color, lw=5)

            #plots the macd and signal line on the second subplot 
            self.axs[1].plot(self.timeData[25:], macd, label='MACD', color='#1E90FF', linewidth=1.5)
            self.axs[1].plot(self.timeData[25:], signalLine, label='Signal Line', color='#FFA500', linewidth=1.5)

            #creates a key to differentiate between macd and signal lines
            self.axs[1].legend(loc="lower left", fontsize=5, markerscale=0.2)

            #plots a bar for each histogram value
            for i in range(len(histogram)):
                #width is split over how much of the x axis is covered and how many bars are needed
                #I decreased the width of each bar by 20% to improve aesthetics
                width = (self.timeData[-1] - self.timeData[25]) / len(histogram) * 0.8
                color = "#00FF00" if histogram[i] > 0 else "#FF0000"
                #plots the bar
                self.axs[1].bar(self.timeData[25 + i], histogram[i], width=width, color=color, alpha=0.3)
            #plots the rsi values in subplot 3
            self.axs[2].plot(self.timeData[25:], rsi, color="#40E0D0", label="RSI")
            #plots the adx values in subplot 4
            self.axs[3].plot(self.timeData[25:], adx, color="#9B4DFF", label="ADX")

            #function definition used to determine buy or sell signal
            def indicatorSignal(macd, signalLine, rsi, adx, time):
                #initialise variables that I will use to see how many of the indicators indicate a buy or sell signal
                buyCount, sellCount = 0, 0

                #based on mathematical conclusions, each of these indicate a buy or sell
                if macd > signalLine:
                    buyCount += 1
                elif macd< signalLine:
                    sellCount += 1
                if rsi > 70:
                    sellCount += 1
                elif rsi < 30:
                    buyCount += 1 
                if adx > 25 and macd > signalLine:
                    buyCount += 1
                elif adx > 25 and macd < signalLine:
                    sellCount += 1
                
                #when all 3 match to either buying or selling, I will notify the user by printing it directly
                #in the terminal
                if buyCount == 3:
                    print("Good Buying point",  time.strftime("%Y-%m-%d %H:%M:%S"))
                    return "Good Buying point",  time.strftime("%Y-%m-%d %H:%M:%S")
                elif sellCount == 3:
                    print("Good Selling point",  time.strftime("%Y-%m-%d %H:%M:%S"))
                    return "Good Selling point",  time.strftime("%Y-%m-%d %H:%M:%S")

           
            try: #if the indicator signal returns values then carry on
                analysis , period = indicatorSignal(macd[-1], signalLine[-1], rsi[-1], adx[-1], self.timeData[-1])
            except: #otherwise there is nothing returned would would cause an error in assignment
                analysis = None
            if analysis != None:
                #if a record exists it will update the analysis and period, otherwise it will create a new record
                addCrypto(self.ticker, period, analysis)

            #manually re draws the whole canvas after each candlestick
            self.after(0, self.canvas.draw)

        
        #if there is an error, it is printed in an easy simple way to help me fix bugs
        except Exception as e:
            print(f"Error in plotting the candlesticks: {e}")


    #this method makes the program terminate safely without causing erros
    def onUserQuit(self):
        #calls on the global flag variable to change its value to False meaning that the next time
        #the websocket tries to take a message, it will stop its execution and quit the program within
        #the websockets onClose() function
        global flag
        flag = False
        #if there is not websocket connection, the program can simply quit, but because I want to run the
        #program more than once within another class, I need to reset the value of flag to True
        if not self.socket:
            self.withdraw()
            flag = True

if __name__ == "__main__":
    #calls the class and runs it with the given parameters
    app = CandlesApp("15m", "BTCUSDT", False)
    app.mainloop()
