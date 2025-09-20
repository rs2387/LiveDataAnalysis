#importing modules / libraries
import customtkinter as ctk
import sys
import requests
import random
from bs4 import BeautifulSoup
#importing functions from my other files
from database import addUser, checkUser, checkPass, validPass, hashPass, verifyPass, updateWatchListDetails
from database import addCompany, checkCompany, trendingWatchlist, extractNews, getWatchlist
from api import getCustomCandles
from sentiment import recent10
#importing a class from my other file
from graph import CandlesApp


#list of all the tickers that are USDT tickers from the uk binance website
tickersUSDT = [
    "ETHUSDT", "BTCUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT",
    "ADAUSDT", "DOGEUSDT", "DOTUSDT", "LTCUSDT", "AVAXUSDT",
    "MATICUSDT", "SHIBUSDT", "LINKUSDT", "ATOMUSDT", "TRXUSDT",
    "ETCUSDT", "XLMUSDT", "NEARUSDT", "BCHUSDT", "ALGOUSDT",
    "VETUSDT", "FILUSDT", "ICPUSDT", "HBARUSDT", "SANDUSDT",
    "EGLDUSDT", "AXSUSDT", "THETAUSDT", "XTZUSDT", "AAVEUSDT",
    "KSMUSDT", "CAKEUSDT", "GRTUSDT", "MKRUSDT", "COMPUSDT",
    "ZILUSDT", "ONTUSDT", "DASHUSDT", "ZECUSDT", "STXUSDT",
    "WAVESUSDT", "CHZUSDT", "ENJUSDT", "BATUSDT", "MANAUSDT",
    "YFIUSDT", "BALUSDT", "CRVUSDT", "1INCHUSDT", "RSRUSDT",
    "LRCUSDT", "OCEANUSDT", "BNTUSDT", "SRMUSDT", "SUSHIUSDT",
    "UNIUSDT", "FTMUSDT", "HNTUSDT", "RENUSDT", "KAVAUSDT",
    "CVCUSDT", "BANDUSDT", "RLCUSDT", "STORJUSDT", "NKNUSDT",
    "DGBUSDT", "SCUSDT", "ANKRUSDT", "CELRUSDT", "CTSIUSDT",
    "DENTUSDT", "HOTUSDT", "MTLUSDT", "OGNUSDT", "STMXUSDT",
    "TROYUSDT", "WRXUSDT", "AKROUSDT", "COTIUSDT", "DOCKUSDT",
    "FUNUSDT", "MBLUSDT", "MITHUSDT", "PERLUSDT", "STPTUSDT",
    "VITEUSDT", "WINUSDT", "XEMUSDT", "XVSUSDT", "ZENUSDT",
    "ZRXUSDT", "ARPAUSDT", "BTSUSDT", "CTKUSDT", "DATAUSDT",
    "DIAUSDT", "FETUSDT", "FLMUSDT", "FORTHUSDT", "GHSTUSDT",
    "JSTUSDT", "KMDUSDT", "LITUSDT", "MDTUSDT", "NBSUSDT",
    "NMRUSDT", "PNTUSDT", "PSGUSDT", "QNTUSDT", "RIFUSDT",
    "SFPUSDT", "SKLUSDT", "SWRVUSDT", "TCTUSDT", "TWTUSDT",
    "UFTUSDT", "UMAUSDT", "UNFIUSDT", "UTKUSDT", "XVGUSDT",
    "ALPHAUSDT", "BELUSDT", "BLZUSDT", "BZRXUSDT", "C98USDT",
    "DEGOUSDT", "DFUSDT", "DODOUSDT", "EPSUSDT", "ERNUSDT",
    "FIROUSDT", "FRONTUSDT", "GNOUSDT", "GRSUSDT", "HARDUSDT",
    "IRISUSDT", "JUVUSDT", "KP3RUSDT", "LINAUSDT", "MBOXUSDT",
    "MDXUSDT", "MINAUSDT", "MIRUSDT", "MOVRUSDT", "POLSUSDT",
    "PORTOUSDT", "PROMUSDT", "QIUSDT", "RAMPUSDT", "REEFUSDT",
    "SANTOSUSDT", "SPELLUSDT", "SUPERUSDT", "TKOUSDT", "TLMUSDT",
    "TORNUSDT", "TRBUSDT", "TVKUSDT", "WINGUSDT", "WNXMUSDT",
    "XECUSDT", "XNOUSDT", "YFIIUSDT", "ZECUSDT", "ZRXUSDT", 
    "KAITOUSDT", "TSTUSDT"
]



#creates the class for the overall app
class CryptoApp:
    #initialising the system
    def __init__(self):
        #root is the parent window, this will be the main window
        self.root = ctk.CTk()
        #instantly calls the function to adjust the root window to act as the login page
        self.setLoginWindow()

    #defines a function to set the login page onto the root window where the
    #user will be asked for details to authorise their access
    def setLoginWindow(self):
        #set the title of the root page
        self.root.title("Login System")
        #set the size of the window to 350 in x and 300 in y
        self.root.geometry("350x300")
        #set the background colour to gray
        self.root.configure(fg_color="gray25")
        #calls the exit app function when the user presses close
        self.root.protocol("WM_DELETE_WINDOW", self.exitApp)

        #creates a label to display the secondary title for the login window
        ctk.CTkLabel(self.root, text="Login System", font=("Helvetica", 18, "bold"),
                        text_color="white").grid(row=0, column=0, columnspan=2, pady=20)

        #creates the username label next to the username textbox 
        ctk.CTkLabel(self.root, text="Username:", font=("Helvetica", 12),
                        text_color="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        #creates the username entry textbox for my users
        self.usernameEntry = ctk.CTkEntry(self.root, width=250, border_width=3,
                                            corner_radius=10, fg_color="white", border_color="purple")
        self.usernameEntry.grid(row=1, column=1, padx=10, pady=5)
        
        #creates the password label next to the password textbox
        ctk.CTkLabel(self.root, text="Password:", font=("Helvetica", 12),
                        text_color="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        #creates the password entry textbox for my users which only shows * for privacy
        self.passwordEntry = ctk.CTkEntry(self.root, show="*", width=250, border_width=3,
                                            corner_radius=10, fg_color="white", border_color="purple")
        self.passwordEntry.grid(row=2, column=1, padx=10, pady=5)

        #creates the login button on the window, commmand calls function to check details inputted by my user
        ctk.CTkButton(self.root, text="Login", command=self.checkCredentials,fg_color="purple",
                        width=200, height=40, corner_radius=10, hover_color="darkviolet", border_width=2,
                        border_color="gold").grid(row=3, column=0, columnspan=2, pady=15)
        
        #creates the signup button on the window, command calls the function to open the register window
        ctk.CTkButton(self.root, text="Register", command=self.openRegisterWindow,
                        fg_color= "purple", width=200, height=40, corner_radius=10,
                        hover_color="darkviolet", border_width=2, border_color="gold").grid(row=4, column=0, columnspan=2, pady=5)

        #creates a feedback label which I will access later to display reponses according to the validity of the credentials
        self.feedbackLabel = ctk.CTkLabel(self.root, text="", font=("Helvetica", 12), text_color="red")
        self.feedbackLabel.grid(row=5, column=0, columnspan=2, pady=5)

    #defines a function called when pressing the login button to check the user's inputted credentials against
    #the saved data in my databases
    def checkCredentials(self):

        #username and password are the values stored in each entry textbox with spaces removed
        username, password = self.usernameEntry.get().strip(), self.passwordEntry.get().strip()

        #check pass is a function that returns a list of usernames and passwords in table users in tuples
        #for each tuple in the list
        for tuple in checkPass():
            #the user entered password is verified against the stored hashed password in the database#
            #the verify pass function returns either true of false for the match
            correctPass = verifyPass(password, tuple[1])
            if username and password: #if both username and password entry are filled
                #if the passwords match, and the username matches the same tuple for that passowrd
                if correctPass == True and username.lower() == str(tuple[0]).lower():
                    #the login has been successful, call the feedback label defined earlier and display success message
                    self.feedbackLabel.configure(text="Login Successful!", text_color="green")
                    #declare username as an attribute so I can use it in other parts of the program
                    self.username = username.lower()
                    #withdraws the login window after 1 mili second
                    self.root.after(100, self.root.withdraw)
                    #call a function to open the main window of the program
                    self.openMainWindow()
                else:
                    #otherwise, the text in the feedback label is just invalid
                    self.feedbackLabel.configure(text="Invalid username or password", text_color="red")
            else: #otherwise inform user that the fields are blank
                self.feedbackLabel.configure(text="Some fields left blank", text_color="red")

    #defines a function to open the main window where the user can choose to access the trending page or the 
    #watchlist page
    def openMainWindow(self):
        #creates a top level window thats basically independant of the main program
        self.mainWindow = ctk.CTkToplevel()  
        #sets the title of the main window to cryptocurrency
        self.mainWindow.title("Cryptocurrency")
        #sets the size of the main window to 400 in x and 250 in y
        self.mainWindow.geometry("400x250")
        #forces the main window to be the focus, even while other windows are closing
        self.mainWindow.focus_force()
        #if the user closes this window, exit the program
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.exitApp)
        #sets the background colour for the main window
        self.mainWindow.configure(fg_color="gray25")
        
        #since the main window can be accessed from the trending window or watchlist and the login window, 
        #an error may occur when trying to withdraw the trending page when it doesn't exist
        try:
            #if the trending window existed, close it
            self.trendingWindow.after(100, self.trendingWindow.withdraw)
        except AttributeError:
            #otherwise carry on as normal
            pass
        try:
            #if the watchlist window existed, close it
            self.watchlistWindow.after(100, self.watchlistWindow.withdraw)
        except AttributeError:
            #otherwise carry on as normal
            pass

        #creates a label for the title for the main window
        ctk.CTkLabel(self.mainWindow, text="Welcome to your Cryptocurrency App!", font=("Helvetica", 14, "bold"),
                        text_color="white").pack(pady=20)
        
        #creates a button on the main window that when pressed, command calls the open trending window function,
        #using the lambda command to pass in a value for the paramter (True)
        ctk.CTkButton(self.mainWindow, text="Trending", command=lambda: self.openTrendingWindow(True), fg_color="purple",
                        width=200, height=40, corner_radius=10, hover_color="darkviolet",
                        border_width = 2, border_color="gold").pack(pady=10)
        
        #creates a button on the main window that when pressed, command calls the open watchlist window function
        ctk.CTkButton(self.mainWindow, text="Watchlist", command=self.openWatchlistWindow, fg_color="purple",
                        width=200, height=40, corner_radius=10, hover_color="darkviolet",
                        border_width = 2, border_color="gold").pack(pady=10)



    #defines a function to open the trending window in one of two modes, trending in the user's company or in 
    #all the external companies excluding the user's company
    def openTrendingWindow(self, mode:bool):
        #creates a top level window thats basically independant of the main program
        self.trendingWindow = ctk.CTkToplevel()
        #titles the trending window as trending now
        self.trendingWindow.title("Trending Now")
        #makes the size 600 in x and 350 in y
        self.trendingWindow.geometry("600x350")
        #forces the program to display this window at the front
        self.trendingWindow.focus_force()
        #manually withdraws the main window after 0.1 seconds to not interrupt gui
        self.mainWindow.after(100, self.mainWindow.withdraw)
        #sets background color of the window
        self.trendingWindow.configure(fg_color="#2C2C2C") 
        #if the user closes this window, exit the program
        self.trendingWindow.protocol("WM_DELETE_WINDOW", self.exitApp)

        #this variable describes whether the trending tickers are within the company or not
        #according to the first parameter passed in which is True from main, this will never change
        inCompany = mode

        #selection to switch between the two modes
        if inCompany == True:
            #the default title for trends in company 
            title = "Your Company Trends"
        elif inCompany == False:
            #the default title for trends outside company 
            title = "Other Company Trends"
        
        #sets up a grid to make placing my widgets and texts easier
        self.trendingWindow.columnconfigure(0, weight=2) #the left side is trending tickers
        self.trendingWindow.columnconfigure(1, weight=1)  #the right side is gainers & losers
        self.trendingWindow.rowconfigure(0, weight=1)  #allows the row to stretch

        #creates a trending frame and aligns it in the grid
        companyTrendingFrame = ctk.CTkFrame(self.trendingWindow, corner_radius=10, fg_color="gray25")
        companyTrendingFrame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        #creates a label to display the title and packs it near the top of the window
        ctk.CTkLabel(companyTrendingFrame, text=title, font=("Helvetica", 20, "bold"), text_color="white").pack(pady=5)

        #calls a function that returns the top three tickers for the user signed in
        #either inCompany is True and it takes the top 3 in the company or its False and it will get the 
        #top 3 outside the company
        top3tickers = trendingWatchlist(self.username, inCompany)

        #for each ticker in the top3 tickers
        for i in range(3):
                
                #remove the suffix usdt to get it ready for the url
                coin = top3tickers[i].removesuffix("USDT")

                #use an f string to get the url I need for each ticker
                tickerURL = f"https://finance.yahoo.com/quote/{coin}-USD/"
                #use headers to stop the server rejecting my request or limitting it
                headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                            "Accept-Language": "en-US,en;q=0.9",
                            "Referer": "https://www.google.com/",
                            "DNT": "1", 
                            "Connection": "keep-alive",
                            "Cache-Control": "no-cache",
                        }
                
                #use requests to get the data from the url I just concatenated
                tickerResponse = requests.get(tickerURL, headers=headers)
                #pass it through a parser to collect html data
                tickersSoup = BeautifulSoup(tickerResponse.content,'html.parser')
                #split the data into certain sections finding the classes with the relevant info
                html1 = tickersSoup.findAll('span',class_='base txt-positive yf-ipw1h0')
                #both these classes had to be found manualy by inspecting the html on the website
                #the only disadvantage is that they might change with time 
                html2 = tickersSoup.findAll('span',class_='base txt-negative yf-ipw1h0')

                #there may be no results for either, so this error checker is used to 
                #make the program more robust
                try:
                    #try slice the list
                    x = html1[1]
                except:
                    #slice the second list since the first is empty which is why it raises an error
                    x = html2[1]

                #I need to select the relevant part of the data I want, so I used some string slicing
                #the start index will be the index after a ">" 
                startIndex = str(x).find(">") + 1 #+1 because its inclusive
                #the end index will be the final "<"
                endIndex = str(x).rfind("<")
                #slice the data and store it as a string data type
                #in this case the data is the percentage change of the day
                percentage = str(x)[startIndex:endIndex]  

                count =0
                while count < 1:
                    #extract positive and negative headlines for each by calling a function to access the database
                    positiveNews = extractNews(top3tickers[i], "Positive")
                    negativeNews = extractNews(top3tickers[i], "Negative")
                    #out of all the available headlines, I randomly take one of each using random library and list indexing
                    try:
                        positiveHeadline= positiveNews[random.randint(0, (len(positiveNews)-1))]
                        negativeHeadline = negativeNews[random.randint(0, (len(negativeNews)-1))]
                        break
                    except:
                        recent10([top3tickers[i]])
                        positiveHeadline, negativeHeadline = "None", "None"
                        count +=1
                #create label to dislay the ticker and its percentage change in the day
                ctk.CTkLabel(companyTrendingFrame, text=top3tickers[i]+' ' +percentage, font=("Helvetica", 14, "bold"), text_color="white").pack( pady=3)
                #creates a button to add any of the trending tickers to your watchlist, and will call a function to update the details in the database
                ctk.CTkButton(companyTrendingFrame,command=lambda: updateWatchListDetails(self.username, top3tickers[i],
                                add=True), text="Add to Watchlist", font=("Helvetica", 6), width=10, height=10, fg_color="purple",
                                hover_color="darkviolet", text_color="white",border_width=1, border_color="gold").place(relx=0.7, rely=0.15+0.287*i)
                #I also had to use the place function to position it to line up with each ticker so it will be moved down relative to each tickers position (i)

                #creates another 2 labels to write in each headline, green for positive, red for negative
                ctk.CTkLabel(companyTrendingFrame, text=positiveHeadline, text_color="green", font=("Helvetica", 12, "bold"), wraplength=325).pack(pady=2)
                ctk.CTkLabel(companyTrendingFrame, text=negativeHeadline, text_color="red", font=("Helvetica", 12, "bold"), wraplength=325).pack(pady=2)
                
                    
        #assigns url to variable called rankings 
        rankingsURL = "https://api.binance.com/api/v3/ticker/24hr"

        #use the binance api to get the data
        response = requests.get(rankingsURL)
        rankingsResponse = response.json()

        #initiliase empty lists for the gainers and losers of the day
        gainers, losers = [], []

        #loop through each ticker's data from the binance response
        for ticker in rankingsResponse:
            try:
                symbol = ticker["symbol"]
                #if USDT isnt in symbol, then the if statement will be true
                #this then calls continue which skips the try clause
                if not "USDT" in symbol:
                    continue

                #use this key to get the price percentage change that I want for each ticker
                percentChange = float(ticker['priceChangePercent'])
                
                #if the percentage change is greater than 0 then append it to gainers
                if percentChange > 0:
                    gainers.append((ticker, percentChange))
                #if the percentage change is less than 0 then append it to losers
                elif percentChange < 0:
                    losers.append((ticker, percentChange))
            except ValueError:
                #handles any errors where the value can't be converted to float, I don't
                #want to stop the program, I just want it to move on without displaying any
                #false data - basically just ignore anything not in format I want
                continue

        #function definition to create a recursive merge sort algorithm, to sort all
        #the percetage changes as quickly as possible, since there are a lot of values
        def mergeSort(unsortedList):
            if len(unsortedList) <= 1:
                return unsortedList

            #set the middle value and recursively breakdown the list
            middle = len(unsortedList) // 2
            #splits the list into 2 using slicing
            leftHalf = unsortedList[:middle]
            rightHalf = unsortedList[middle:]

            #recursively calling the function
            sortedLeft = mergeSort(leftHalf)
            sortedRight = mergeSort(rightHalf)

            #returns a sorted section of each left and right
            return merge(sortedLeft, sortedRight)

        #function definition to combine the two seperately sorted lists
        def merge(left, right):
            result = []
            i = j = 0

            #they need to be ordered in terms of percentage changes which is index 1 in the tuple
            while i < len(left) and j < len(right):
                #if that index from each left or right side is greater append it
                if left[i][1] < right[j][1]:  
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1

            #the extend function just appends all the remaining values on the list
            result.extend(left[i:])
            result.extend(right[j:])

            return result

        #call merge sort for each of these lists
        top3gainers = mergeSort(gainers)[-3:] #the last three (the three most positive)
        top3losers = mergeSort(losers)[:3] #the first three (the three most negative)

        #initialise empty lists to get data in a list format that I wanted
        displayGainers, displayLosers = [], []
        #I did this so I could just join each value with \n and have it line by line

        for i in range(3):
            #there are only 3 tickers in each, empty lists are using f strings
            #top3gainers starts from the 3rd and goes down since its hte highest number
            displayGainers.append(f"{top3gainers[2-i][0]['symbol']}: {top3gainers[2-i][1]}%")
            #top3losers is the opposite and is at the start i = 0
            displayLosers.append(f"{top3losers[i][0]['symbol']}: {top3losers[i][1]}%")


        #creates a frame that will be used to display all the top gainers or losers for the day
        gainersLosersFrame = ctk.CTkFrame(self.trendingWindow, corner_radius=10, fg_color="grey25")
        #uses grid function to lay it out in an orderly manner
        gainersLosersFrame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        #creates a label to display the top gainers title within the previously built frame
        ctk.CTkLabel(gainersLosersFrame, text="Top Gainers 📈 ", text_color="green", font=("Helvetica", 15, "bold")).pack(pady=5)
        #creates a label to display the top gainers headlines within the previously built frame
        ctk.CTkLabel(gainersLosersFrame, text="\n".join(displayGainers), font=("Helvetica", 12), text_color="white").pack(pady=5)

        #creates a label to display the top losers title within the previously built frame
        ctk.CTkLabel(gainersLosersFrame, text="Top Losers 📉 ", text_color="red", font=("Helvetica", 15, "bold")).pack(pady=5)
        #creates a label to display the top losers headlines within the previously built frame
        ctk.CTkLabel(gainersLosersFrame, text="\n".join(displayLosers), font=("Helvetica", 12), text_color="white").pack(pady=5)
        
        #creates a button to switch modes, it will close and reopen the trending window with the not boolean value of inCompany
        ctk.CTkButton(self.trendingWindow, text="Switch Modes", command=lambda: [ self.trendingWindow.after(0, self.trendingWindow.withdraw), self.openTrendingWindow((not inCompany))],  fg_color="purple",
                    width=85, height=20, corner_radius=5, hover_color="darkviolet",
                    border_width=1, border_color="gold").place(relx=0.780, rely=0.7)
        #creates a button that calls a function to open the main window that acts as a back button
        ctk.CTkButton(self.trendingWindow, text="Back", command=self.openMainWindow, fg_color="purple",
                    width=80, height=15, corner_radius=5, hover_color="darkviolet",
                    border_width=1, border_color="gold").place(relx=0.794, rely=0.8)    

    
    def openWatchlistWindow(self): 
        #creates a top level window thats basically independant of the main program 
        self.watchlistWindow = ctk.CTkToplevel()
        #sets the title of this window
        self.watchlistWindow.title("Your Watchlist")
        #makes the size 450 in x and 520 in y
        self.watchlistWindow.geometry("450x520")
        #forces the program to display this window at the front
        self.watchlistWindow.focus_force()
        #if the user closes this window, exit the program
        self.watchlistWindow.protocol("WM_DELETE_WINDOW", self.exitApp)
        #sets the background colour
        self.watchlistWindow.configure(fg_color="#2C2C2C")

        #manually withdraws the main window after 0.1 seconds
        self.mainWindow.after(100, self.mainWindow.withdraw)
        #if the crypto window was previously opened, it will be closed
        try:
            #will raise an error if crypto window had not previously been open
            self.cryptoWindow.after(100, self.cryptoWindow.withdraw)
        except:
            pass


        #call a function that will get the all the tickers in the user's watchlist
        self.watchlist = getWatchlist(self.username)
        
        self.pageIndex = 0  #this page index will be used to organise the tickers into seperate pages

        #creates an entrybox that the user will use to add a ticker to their watchlist
        self.tickerSearchInput = ctk.StringVar()
        searchEntry = ctk.CTkEntry(self.watchlistWindow, textvariable=self.tickerSearchInput,
                                    placeholder_text="Search ticker...", placeholder_text_color="black")
        searchEntry.pack(pady=5)

        #creates a label to display an error message if the user tries to add a duplicate or not existent ticker
        self.errorLabel = ctk.CTkLabel(self.watchlistWindow, text="", text_color="red", font=("Helvetica", 12))
        self.errorLabel.pack(pady=0)
        
        #creates a button to add each ticker to a watchlist, and it calls the updateWatchListDisplay function
        ctk.CTkButton(self.watchlistWindow, text="Add to Watchlist", command=self.updateWatchlistDisplay, 
            fg_color="purple", width=80, height=15, corner_radius=5, hover_color="darkviolet",border_width=2,
            border_color="gold").pack(pady=5)

        #creates a frame to display the watchlist tickers in an organised way
        self.watchlistFrame = ctk.CTkFrame(self.watchlistWindow, fg_color="gray25")
        self.watchlistFrame.pack(pady=10, fill="y", expand=True)

        #creates a frame to organise the next and back buttons
        buttonFrame = ctk.CTkFrame(self.watchlistWindow, fg_color="#2C2C2C")
        buttonFrame.pack(pady=10)

        #creates a button to go to the next set of tickers in the watchlist
        #command calls a function to do this manually
        ctk.CTkButton(buttonFrame, text="Next", command=self.nextTickers, fg_color="purple", width=80, height=15,
            corner_radius=5,hover_color="darkviolet", border_width=1, border_color="gold").pack(side="left", padx=5)

        #creates a button to go back, where command calls function to open the main window 
        ctk.CTkButton(buttonFrame, text="Back", command=self.openMainWindow, fg_color="purple", width=80, height=15,
            corner_radius=5,hover_color="darkviolet", border_width=1, border_color="gold").pack(side="right", padx=5)

        #calls the function to update the current display
        self.updateWatchlistDisplay()

    #defines a function to update the watchlist display
    def updateWatchlistDisplay(self):
        #if the ticker the user entered with some added validation and error handling is in the list
        #of accepted tickers, then my program will add it to their watchlist
        if self.tickerSearchInput.get().strip().upper() in tickersUSDT:
            #calls a function to update the database adding the ticker to the user's watchlist
            updateWatchListDetails(self.username,  self.tickerSearchInput.get().strip().upper(), True)
            self.errorLabel.configure(text="")  #clears any previous error message
        else:
            #otherwise, the ticker will be invalid and will display an error message
            self.errorLabel.configure(text="Invalid ticker", text_color="red")

        #for each widget within the watchlist frame (meaning each ticker in the watchlist
        #currently being displayed)
        # .winfo_children is a tkinter function that returns a list of all the child widgets in the parent
        for widget in self.watchlistFrame.winfo_children(): 
            widget.destroy() #destroy it as it will be replaced

        #redefines the visible tickers as the next 3 tickers not previously displayed
        visibleTickers = self.watchlist[self.pageIndex:self.pageIndex + 3]
        
        #if there are no tickers in the watchlist
        if not visibleTickers:
            #create a label saying that to the user
            ctk.CTkLabel(self.watchlistFrame, text="No tickers in watchlist", text_color="white").pack()
            return
        
        
        #creates a button for each ticker as well as displaying 3 random positive and negative headlines
        for ticker in visibleTickers:
            #checks to make sure the ticker is not empty
            if ticker == '':
                pass
            #if it is a valid ticker
            else:
                #call the function to extract all the headlines fot that ticker where the sentiment
                #is positive and negative and store respectively
                positiveNews = extractNews(ticker, "Positive")
                negativeNews = extractNews(ticker, "Negative")

                #use the random.sample function to choose a random 3 out of all the headlines
                positiveSampleHeadlines = random.sample(positiveNews, min(3, len(positiveNews)))
                negativeSampleHeadlines = random.sample(negativeNews, min(3, len(negativeNews)))

                #join each headline onto a new line in one string, and if none available then say that
                positiveHeadlinesText = "\n".join(positiveSampleHeadlines[:3]) if positiveSampleHeadlines else "No headlines available"
                negativeHeadlinesText = "\n".join(negativeSampleHeadlines[:3]) if negativeSampleHeadlines else "No headlines available"

                #creates a button for each ticker when pressed calling a commmand to call the 
                #open crypto window function that will display the individual in depth analysis.
                ctk.CTkButton(self.watchlistFrame, text=ticker, command=lambda ticker=ticker: self.openCryptoWindow(ticker),
                    fg_color="purple", text_color="white", width=120, height=25, corner_radius=5,
                    hover_color="darkviolet", border_width=1, border_color="gold").pack(pady=5)
                
                #creates labels to display both the positive and negative headlines seperately
                ctk.CTkLabel(self.watchlistFrame, text=positiveHeadlinesText, font=("Helvetica", 10),
                    text_color="green", wraplength=400).pack(pady=1)
                ctk.CTkLabel(self.watchlistFrame, text=negativeHeadlinesText, font=("Helvetica", 10),
                    text_color="red", wraplength=400).pack(pady=1)

    #defines a function that will switch pages to display the remaining tickers in the watchlist
    def nextTickers(self):
        if self.watchlist: #if the watchlist isnt empty, apply mod to it to alternate between all tickers
            self.pageIndex = (self.pageIndex + 3) % len(self.watchlist)
        self.updateWatchlistDisplay()

    def openLiveChart(self, ticker):   

        try: #if this raises an error it means there is no indicator window
            #if not the window will be closed to prevent duplicate windows
            self.indicatorWindow.withdraw()
        except: #otherwise it will open as normal
            pass

        #creates a top level window that is basically independant of the program
        self.indicatorWindow = ctk.CTkToplevel()
        #sets the title of the window to indicaor support
        self.indicatorWindow.title("Indicator support")
        #sets the size of the window to 450 in x and 310 in y
        self.indicatorWindow.geometry("450x310")
        #sets the background colour to gray
        self.indicatorWindow.configure(fg_color="gray25")
        #if thew window is closed, it just withdraws the window without closing anything else
        self.indicatorWindow.protocol("WM_DELETE_WINDOW", self.indicatorWindow.withdraw)

        #tips to help the user use the indicator data on the chart
        explanationText = (
            "RSI (Relative Strength Index):\n"
            "Buy signal when RSI is *less than 30* (oversold, could reverse upwards).\n"
            "Sell signal when RSI is *greater than 70* (overbought, could pull backwards).\n"
            "Divergence: if the price makes a new high/low and RSI doesn't, the trend is weakening.\n"

            "MACD (Moving Average Convergence Divergence):\n"
            "Buy signal when MACD crosses *above* signal line (bullish momentum).\n"
            "Sell signal when MACD crosses *below* signal line (bearish momentum).\n"
            "Zero-Line Crossover: greater than 0 zero is bullish, less than zero is bearish.\n"
            "Divergence: confirms potential reversals.\n"

            "ADX (Average Directional Index):**\n"
            "Trend Strength: Above 25 = strong trend, below 20 = weak/sideways.\n"
            "Buy signal when ADX is *greater than 25* when +DI > -DI (uptrend).\n"
            "Sell signal when ADX *greater than 25* when -DI > +DI (downtrend).\n"
            "Trend Strength: Above 25 = strong trend, below 20 = weak/sideways."
        )
        
        #creates a label with the explanation text inside it
        ctk.CTkLabel(self.indicatorWindow, text=explanationText, font=("Helvetica", 12),
                      text_color="white", wraplength=400).pack(pady=10)
        #creates a button that when pressed will withdraw the window
        ctk.CTkButton(self.indicatorWindow, text="Close", command=self.indicatorWindow.withdraw,
                      fg_color="purple", width=80, height=15, corner_radius=5, hover_color="darkviolet",
                      border_width=2, border_color="gold").pack(pady=0)

        interval = self.intervalInput.get() #gets the interval from the dropdown menu previously
        #if the interval is one of the ones in the list, a socket is needed to allow live price change
        needed = True if interval in ["1s","5s", "10s","15s","1m", "2m", "5m"] else False 

        #calls the CandlesApp class with the given parameters to display the candlestick chart
        if __name__ == "__main__":
            #this new app acts as a standalone program which is perfect because I do not want any
            #interference between the graph plotting and the user interface
            app = CandlesApp(interval=interval, ticker=ticker, socketNeeded=needed)
            app.mainloop()
   

    def openCryptoWindow(self, ticker: str):
        #creates a top level window that is basically independant of the rets of the program
        self.cryptoWindow = ctk.CTkToplevel()
        #sets the title of the window to the raw ticker's breakdown
        self.cryptoWindow.title(f"{ticker.removesuffix('USDT')} Breakdown")
        #sets the size of the window to 650 in x and 300 in y
        self.cryptoWindow.geometry("650x300")
        #after 0.2 seconds will withdraw the watchlist window
        self.watchlistWindow.after(200, self.watchlistWindow.withdraw)
        #will force the crypto windo wto be the focus
        self.cryptoWindow.focus_force()     
        #sets the background colour to a hex value (a type of gray)
        self.cryptoWindow.configure(fg_color="#2C2C2C")
        #if the window is closed, the program will terminate
        self.cryptoWindow.protocol("WM_DELETE_WINDOW", self.exitApp)

        #a list of all the possible intervals for display
        allIntervals = ["1s", "5s", "10s", "15s", "1m", "2m", "5m", "15m", "30m", "1h",
                        "4h", "6h", "8h", "12h", "1d", "1w", "1M"]

        #configures rows and columns to layout and organise the information more easily
        self.cryptoWindow.columnconfigure(0, weight=2)  #used to display news
        self.cryptoWindow.columnconfigure(1, weight=1)  #used to display buttons
        self.cryptoWindow.rowconfigure(0, weight=1)

        #call a function to actually scrape the most recent headlines and find their sentiments,
        #unlike the previous functions that extracted the headlines from the database
        total, scores = recent10([ticker.removesuffix("USDT")])
        #scores is the all the probabilities of each headline added up together
        if scores/10 > 0.1: #if the average is greater than 0.1 then positive
            score = "Positive"
            scoreColour = "Green"
        elif scores/10 < -0.1: #if the average is less than 0.1 then negative
            score = "Negative"
            scoreColour = "Red"
        else: 
            score = "Neutral"
            scoreColour = "White"
        if total == []:
            total = ["No headlines found"]

        #create a frame to display the headlines
        newsFrame = ctk.CTkFrame(self.cryptoWindow, fg_color="gray25")
        newsFrame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        #create a label inside the news frame to display the overall sentiment for the past 10 headlines
        ctk.CTkLabel(newsFrame, text=f"Overall sentiment for most recent articles is: {score}", font=("Helvetica", 14, "bold"),
                      text_color=scoreColour, wraplength=450, anchor="w").pack(padx=10, pady=5)
        #create a label inside the news frame to display all the headline text 
        ctk.CTkLabel(newsFrame, text="\n".join(total), font=("Helvetica", 12), text_color="white",
                      wraplength=400, anchor="w").pack(padx=10, pady=5)

        #create a frame for all the buttons on the right hand side of the window
        buttonsFrame = ctk.CTkFrame(self.cryptoWindow, fg_color="gray25")
        buttonsFrame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        #create a button to remove the ticker from watchlist
        #command calls the function with a False parameter meaning the record will be deleted from the database
        ctk.CTkButton(buttonsFrame, text="Remove from Watchlist", command=lambda: updateWatchListDetails(self.username, ticker, False),
                      fg_color="purple", width=80, height=15, corner_radius=5, hover_color="darkviolet",
                      border_width=2, border_color="gold").pack(pady=10)
        
        #this function will only return the intervals for whcih the api has returned valid data
        def filterIntervals():
            #empty list of possible intervals
            possibleIntervals=[]
            #loop through each interval available 
            for interval in allIntervals:
                if interval in ["1s", "5s", "10s", "15s", "1m", "2m", "5m", "15m"]:
                    #for the intervals needing sockets, loop through set values to variables
                    intervalSeperation = int(interval[:-1]) #just the number part of each 
                    tempInterval = "1m" if interval[-1] == "m" else "1s"
                    totalCandles = 65
                else:
                    totalCandles = 85
                    intervalSeperation = 1
                    tempInterval = interval
                #for each interval, call a function to get the data needed to display the chart
                try:
                    getCustomCandles(ticker, tempInterval, intervalSeperation, totalCandles)
                    #if succesful, append that interval to the possible intervals list
                    possibleIntervals.append(interval)
                #when the data is not available, simply pass 
                except ImportError:
                    pass
            return possibleIntervals #returns a list of all the working intervals
        
        #call a function to filter the intervals 
        possibleIntervals = filterIntervals()
        
        #creates a dropdown option menu with all the intervals possible within the button frame
        self.intervalInput = ctk.StringVar(value="15m") #sets default value to 15m
        self.intervalMenu = ctk.CTkOptionMenu(buttonsFrame, values=possibleIntervals,
                                            variable=self.intervalInput, fg_color="purple", corner_radius=10,
                                            button_hover_color="darkviolet", dropdown_fg_color="purple",
                                            button_color="purple", dropdown_hover_color="darkviolet",
                                            dropdown_text_color="white")
        #this menu also automatically changes the variable self.intervalInput to the selected value
        self.intervalMenu.pack(pady=10, padx=10)

        #creates a button in button frame with the command that calls the open live chart function to
        #display the candlestick chart for the given ticker
        ctk.CTkButton(buttonsFrame, text="Open Live Chart", command= lambda: self.openLiveChart(ticker),
                      fg_color="purple", width=80, height=15, corner_radius=5, hover_color="darkviolet",
                      border_width=2, border_color="gold").pack(pady=10)    
        #creates a button in button frame with the command to open the watchlist window when it's pressed
        ctk.CTkButton(buttonsFrame, text="Back", command=self.openWatchlistWindow, fg_color="purple",
                      width=80, height=15, corner_radius=5, hover_color="darkviolet", border_width=2,
                      border_color="gold").pack(pady=10)

    #this function opens the window for the user to register within the system and create a record in table users
    def openRegisterWindow(self):
        #creates a top level window that is basically independant of the program
        self.registerWindow = ctk.CTkToplevel()
        #sets the title of the window to register
        self.registerWindow.title("Register")
        #sets the size of the window to 400 in x and 300 in y
        self.registerWindow.geometry("400x300")
        #forces the window to be the focus
        self.registerWindow.focus_force()
        #after 0.1 seconds close the login window
        self.root.after(100, self.root.withdraw)
        #if the user closes this window, exit the program
        self.registerWindow.protocol("WM_DELETE_WINDOW", self.exitApp)
        #sets background and theme for the register window
        self.registerWindow.configure(fg_color="gray25")

        #creates a label to display the title for the register window
        ctk.CTkLabel(self.registerWindow, text="Register New User", font=("Helvetica", 16, "bold"),
                        text_color="white").grid(row=0, column=0, columnspan=2, pady=20)

        #creates a label for the new username  text
        ctk.CTkLabel(self.registerWindow, text="New Username:", font=("Helvetica", 12),
                        text_color="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        #creates a username entry textbox for new users
        usernameEntry = ctk.CTkEntry(self.registerWindow, width=250, border_width=3,
                                        corner_radius=10, fg_color="white", border_color="purple")
        usernameEntry.grid(row=1, column=1, padx=10, pady=5)

        #creates a label for the password text
        ctk.CTkLabel(self.registerWindow, text="New Password:", font=("Helvetica", 12),
                        text_color="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        #creates a password entry textbox for new users 
        password1Entry = ctk.CTkEntry(self.registerWindow, width=250,show="*", border_width=3,
                                        corner_radius=10, fg_color="white", border_color="purple")
        password1Entry.grid(row=2, column=1, padx=10, pady=5)

        #creates a label for the confirm password text
        ctk.CTkLabel(self.registerWindow, text="Confirm Password:", font=("Helvetica", 12),
                        text_color="white").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        #creates a confirm password entry textbox for new users
        password2Entry = ctk.CTkEntry(self.registerWindow,  width=250,show="*", border_width=3,
                                        corner_radius=10, fg_color="white", border_color="purple")
        password2Entry.grid(row=3, column=1, padx=10, pady=5)

        #creates a label placed in a grid where the error and accept messages will be placed
        feedbackLabel = ctk.CTkLabel(self.registerWindow, text="", font=("Helvetica", 12), text_color="red")
        feedbackLabel.grid(row=6, column=0, columnspan=2, pady=10)

        #registers the user by creating a record in table users using the inputs form register window
        def registerUser():
            #gets all the values inputted by the user from the entry boxes
            newUsername = usernameEntry.get().strip()
            newPassword = password1Entry.get().strip()
            confirmPassword = password2Entry.get().strip()

            #checks to see if the username exists in the table already
            checkExists = any(str(user[0]).lower() == newUsername.lower() for user in checkUser())

            #validation for password and username
            #each selection takes a different case and writes a message into the feedback label 
            if not newUsername or not newPassword or not confirmPassword:
                feedbackLabel.configure(text="All fields are required!", text_color="red")
            elif newPassword != confirmPassword:
                feedbackLabel.configure(text="Password do not match", text_color="red")
            elif checkExists == True:
                feedbackLabel.configure(text="Username already exists!", text_color="red")
            #calls valid pass function which returns (True or False, feedback message)
            elif validPass(newPassword, newUsername)[0] == False:
                feedbackLabel.configure(text=validPass(newPassword, newUsername)[1], text_color="red")
            else:
                #if password passes all requirements, open the next window to log company records
                feedbackLabel.configure(text="Registration successful!", text_color="green")
                self.openCompanyWindow(newUsername, newPassword)

        #creates the register button that when pressed command calls function to register them in database
        ctk.CTkButton(self.registerWindow, text="Register", command=registerUser, fg_color="purple",
                        width=200, height=40, corner_radius=10, hover_color="darkviolet", border_width=2,
                        border_color="gold").grid(row=5, column=0, columnspan=2, pady=15)


    #function to connect each user to a certain company
    def openCompanyWindow(self, newUsername, newPassword):
        #creates a top level window that is basically independant of the program
        companyWindow = ctk.CTkToplevel()
        #sets the title of the window 
        companyWindow.title("Register part 2")
        #sets the size of the window to 400 in x and 300 in y
        companyWindow.geometry("400x300")
        #forces the program to focus this window over others
        companyWindow.focus_force()
        #closes the register window after 0.1 seconds
        self.registerWindow.after(100, self.registerWindow.withdraw)
        #if the user closes this window, exit the program
        companyWindow.protocol("WM_DELETE_WINDOW", self.exitApp)
        #sets the background colour of the window
        companyWindow.configure(fg_color="gray25")

        #creates a label with the add company details text
        ctk.CTkLabel(companyWindow, text="Add Company Details", font=("Helvetica", 16, "bold"),
                        text_color="white").grid(row=0, column=0, columnspan=2, pady=20)

        #creates a label to display company name text
        ctk.CTkLabel(companyWindow, text="Company Name:", font=("Helvetica", 12),
                        text_color="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        #creates an entry textbox for the user to input the company name
        companyEntry = ctk.CTkEntry(companyWindow, width=250, border_width=2,
                                        corner_radius=10, fg_color="white", border_color="purple")
        companyEntry.grid(row=1, column=1, padx=10, pady=5)

        #creates a label to display company name text
        ctk.CTkLabel(companyWindow, text="Company CEO:", font=("Helvetica", 12),
                        text_color="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        #creates an entry textbox for the user to input the company name
        CEOentry = ctk.CTkEntry(companyWindow, width=250, border_width=2,
                                        corner_radius=10, fg_color="white", border_color="purple")
        CEOentry.grid(row=2, column=1, padx=10, pady=5)

        #creates a label to display error or success messages
        companyLabel = ctk.CTkLabel(companyWindow, text="", font=("Helvetica", 12), text_color="red")
        companyLabel.grid(row=6, column=0, columnspan=2, pady=10)
        
        #defining a function to register the company inputted within registration process in database
        def registerCompany():
            #company and CEO name from the entry textboxes
            companyName, CEOname = companyEntry.get().strip(), CEOentry.get().strip()
            companies = checkCompany() #calls a function to return all companies and CEO's in database
            limit = False #set limit as False
            #validation similar to password validation
            if not companyName  or  not CEOname :
                #displays error message and allows user to try again
                companyLabel.configure(text="All fields must be filled!", text_color="red")
            else:
                for company in companies: #loops through each company in the database
                    if company[0] == companyName and company[1] == CEOname:
                        companyID = company[2] #if the company exists set the the ID as part of user's record
                        addUser(str(newUsername).lower(), hashPass(newPassword), companyID)
                        limit = True #set limit to True
                        #return a registration successful message in the label
                        companyLabel.configure(text="Registration successful!", text_color="green")
                        companyWindow.after(100, companyWindow.destroy) #close the company window 
                        self.root.deiconify() #open the login window
                        break
                    #if the company name is there but the user entered a differen CEO
                    elif company[0] == companyName and company[1] != CEOname:
                        limit = "details error" #set limit to details error
                        break
                #if the user entered a new company
                if limit == False:
                    addCompany(companyName, CEOname) #create a new company record in database
                    companies = checkCompany() #get all the companies in the database
                    #get the ID of the last company in the list which will be the one I just added 
                    companyID = companies[len(companies)-1][2] 
                    #use that ID when creating the user's record in table User
                    addUser(newUsername, hashPass(newPassword), companyID)
                    #show a registration success message in the label
                    companyLabel.configure(text="Registration successful!", text_color="green")
                    companyWindow.after(100, companyWindow.destroy) #close the company window
                    self.root.deiconify() #open the login window
                elif limit == "details error": #if the details were incorrect
                    #display an error message in the label and allow user to try again
                    companyLabel.configure(text="Company details incorrect", text_color="red")

    


        #creates a button with command calling a function that will register the company in the database
        ctk.CTkButton(companyWindow, text="Finish", command=registerCompany, fg_color="purple",
                        width=200, height=40, corner_radius=10, hover_color="darkviolet", border_width=2,
                        border_color="gold").grid(row=5, column=0, columnspan=2, pady=15)
        
    #terminates/ ends the system when any window is closed by the user
    def exitApp(self):
        sys.exit()

#runs the program
if __name__ == "__main__":
    #calls the cryptoApp class
    app = CryptoApp()
    #runs the class forever
    app.root.mainloop()
    