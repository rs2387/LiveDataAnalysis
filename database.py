#importing modules / libraries
import sqlite3
import re
import bcrypt

#establish a connection between my code and my database in sqlite personal
connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
#establish a cursor object to allow me to perform actions remotely on my database
cursor = connection.cursor()

#define a function to create all my tables
def createTables():
    #table users with all its fields and data types/ validation, primary key and foreign key
    table1 = """CREATE TABLE IF NOT EXISTS [tblUsers](
    [UserID]            INTEGER PRIMARY KEY AUTOINCREMENT,   
    [Username]          TEXT(15) NOT NULL UNIQUE,
    [HashedPassword]    TEXT NOT NULL,
    [CompanyID]         INTEGER NOT NULL,
    FOREIGN KEY (CompanyID) REFERENCES tblCompany (CompanyID)
    )
    """

    #table watch list details with all its fields and data types / validation, primary key
    #and foreign key
    table2 = """CREATE TABLE IF NOT EXISTS [tblWLDetails](
    [WLDetailsID]        INTEGER PRIMARY KEY AUTOINCREMENT,   
    [UserID]             INTEGER NOT NULL,
    [Ticker]             TEXT(10) NOT NULL,
    FOREIGN KEY (UserID) REFERENCES tblUsers (UserID),
    FOREIGN KEY (Ticker) REFERENCES tblCrypto (Ticker)
    )
    """

    #table company with all its fields and data types / validation and primary key
    table3 = """CREATE TABLE IF NOT EXISTS [tblCompany](
    [CompanyID]         INTEGER PRIMARY KEY AUTOINCREMENT,   
    [Name]              TEXT(20) NOT NULL UNIQUE,
    [CEO]               TEXT(20) NOT NULL
    )
    """


    #table cryptocurrency with all its fields and data types / validarion and primary key
    table4 = """CREATE TABLE IF NOT EXISTS [tblCrypto](
    [Ticker]            TEXT(10) PRIMARY KEY,   
    [TimePeriod]        TIME,
    [Analysis]          TEXT(15) 
    )
    """

    #table news with all its fields and data types / validation and primary key and 
    #foreign key
    table5 = """CREATE TABLE IF NOT EXISTS [tblNews](
    [NewsID]             INTEGER PRIMARY KEY AUTOINCREMENT,   
    [Ticker]             TEXT(7) NOT NULL,
    [Headline]           TEXT(50) NOT NULL,
    [Time]               TIME NOT NULL,
    [Date]               DATE NOT NULL,
    [Sentiment]          TEXT(15) NOT NULL,
    FOREIGN KEY (Ticker) REFERENCES tblCrypto (Ticker)
    )
    """

    #create a list of all the tables
    tables = [table1, table2, table3, table4, table5]
    #use a for loop to execute their creation one after the other
    for table in tables:
        cursor.execute(table)


    #saves the changes I made to my database
    connection.commit()




#function definition to add a user to my database when they register
def addUser(username: str, hashedPass: str, companyID: str):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = """ INSERT INTO tblUsers (Username, HashedPassword, CompanyID) 
                VALUES (?, ?, ?)"""
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query, (username, hashedPass, companyID))
    connection.commit()

#function definition to extract data used to check if a company exists or not
def checkCompany():
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = """ SELECT Name, CEO, CompanyID
                FROM tblCompany """
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query)
    return cursor.fetchall()

#function definition to extract tickers in a user's watchlist 
def getWatchlist(username:str):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = """ SELECT tblWLDetails.Ticker
                FROM tblWLDetails, tblUsers
                WHERE tblWLDetails.UserID = tblUsers.UserID AND tblUsers.Username = ? """
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query, (username, ))
    watchListTickers = [] #empty list of tickers in the watchlist
    for ticker in cursor.fetchall(): #append each value into the list
        watchListTickers.append(ticker[0])
    return watchListTickers #return all tickers in the user's watchlist





#function definition to add a crytpo record to the database
def addCrypto(ticker, timePeriod, analysis ):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()

    #select all tickers from table crypto
    cursor.execute("""SELECT * 
                   FROM tblCrypto WHERE Ticker = ?""", (ticker,))
    result = cursor.fetchone()

    if result:  #if a record already exists for that ticker, update it
        cursor.execute("""UPDATE tblCrypto SET  TimePeriod = ?, Analysis = ? 
                       WHERE Ticker = ?""", (timePeriod, analysis, ticker))
    else:  #otherwise add a new record
        cursor.execute("""INSERT INTO tblCrypto (Ticker, TimePeriod, Analysis)
                        VALUES (?, ?, ?)""", (ticker, timePeriod, analysis))
    
    connection.commit()

#function definition to add a company record to table company
#this will only happen after my program has checked for duplicates
def addCompany(companyName, CEOname):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = """ INSERT INTO tblCompany (Name, CEO) 
                VALUES (?, ?)"""
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query, (companyName, CEOname))
    connection.commit()

#function definition to add a watch list detail for a user
def updateWatchListDetails(username, ticker, add:bool):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query1 = """SELECT tblWLDetails.UserID, tblWLDetails.Ticker
                FROM tblWLDetails, tblUsers
                WHERE tblWLDetails.UserID == tblUsers.UserID AND tblUsers.Username = ? """
    cursor.execute(query1, (username,))
    watchListTickers = [] #creates an empty list to be used to store all the tickers from the query
    for tuple in cursor.fetchall(): #append every ticker to the list
        watchListTickers.append(tuple[1])
    if add == True: #add being True adds a ticker to the user's watchlist in the database
        if ticker not in watchListTickers: #to prevent duplicate tickers in a users watchlist
            query2 = """ INSERT INTO tblWLDetails (UserID, Ticker) 
                        VALUES ((SELECT UserID FROM tblUsers WHERE Username = ?), ?)"""
            #executes my sql query and retrieves all the rows as a result of the query
            cursor.execute(query2, (username, ticker))
            connection.commit()
        else:
            #if the ticker is already in the user's details, print already there
            print("already there")
    elif add == False: #add being False removes a ticker from the user's watchlist in the database
        if ticker in watchListTickers: #if the ticker is there, it can be deleted
            query2 = """DELETE FROM tblWLDetails
                        WHERE UserID = (SELECT UserID FROM tblUsers WHERE Username = ?)
                        AND Ticker = ?"""
            #executes my sql query and deletes all the rows as a result of the query
            cursor.execute(query2, (username, ticker))
            connection.commit()
        else: #otherwise I am trying to delete data that is not there
            print("not there")


#function definition to extract data used to check if a user exists or not
def checkUser():
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = """ SELECT Username
                FROM tblUsers """
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query)
    return cursor.fetchall()

#function definition to extract the most recent recommended trade for a given ticker
def checkTrades(ticker):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = """ SELECT Analysis, TimePeriod
                FROM tblCrypto
                WHERE ticker = ? """
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query, (ticker,))
    return cursor.fetchall()

#function definition to extract data needed to check login details
#username and hashed password from record will be checked against the users input values
def checkPass():
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = """ SELECT Username, HashedPassword
                FROM tblUsers """
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query)
    return cursor.fetchall()

#function definition to extract all tickers that are saved under users' watchlists from the same
#company that the current user is from or from all the other companies
#this will be determined using the boolean parameter company
def trendingWatchlist(username:str, company:bool):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    #the user's username will be made an attribute in the large class so is easily accessible
    #use a query to find the company ID of the user
    query1 =f"""SELECT CompanyID
                FROM tblUsers
                WHERE Username = (?) """
    cursor.execute(query1, (username,))
    #take the first value of the list and the first value of the tuple and make sure its an integer
    companyID = int(cursor.fetchall()[0][0])
    #use the company ID to find the tickers that other users with the same company ID have in their watchlists
    #company boolean value is True,so the SQL query extracts those in the same company
    if company == True:
        query2 = f""" SELECT tblWLDetails.Ticker
                    FROM tblUsers, tblWLDetails
                    WHERE tblUsers.CompanyID = ? AND tblUsers.UserID = tblWLDetails.UserID """
    #company boolean value is False,so SQL query extracts those in other companies
    elif company == False:
        query2 = f""" SELECT tblWLDetails.Ticker
                    FROM tblUsers, tblWLDetails
                    WHERE tblUsers.CompanyID != ? AND tblUsers.UserID = tblWLDetails.UserID """
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query2, (companyID,))

    #two lists, one for all the times the ticker appears, one for unique tickers
    tickers, uniqueTickers= [], []

    #loop through the query's return to get all the rows seperately and extract the ticker 
    for record in cursor.fetchall():
        #the ticker is the first index of the tuple, since its the only thing I selected from each row
        tickers.append(record[0])
        if record[0] not in uniqueTickers:
            uniqueTickers.append(record[0])
    
    #the next part of this function will find the 3 most popular tickers, and if there are not enough 
    #tickers in each persons watchlist, then they will be set to default values with no repeats

    defaultTickers = ['BTCUSDT', 'XRPUSDT', 'ETHUSDT']

    #the first case is if the watch list is empty
    if len(uniqueTickers) == 0: 
        top3tickers = defaultTickers
    #the second case is if there is only one ticker in the list
    elif len(uniqueTickers) == 1: 
        possibleDefaults = []
        #checks to see if the one ticker appears in the default tickers
        for ticker in defaultTickers:
            if ticker != tickers[0]: 
                #append to the list if they are not the same
                possibleDefaults.append(ticker)
        #whatever the outcome, it will just take the first two possible default tickers,
        #even if all 3 are available
        top3tickers = uniqueTickers + possibleDefaults[:2] 
    #the third case is if there are two tickers in the list
    elif len(uniqueTickers) == 2: 
        possibleDefaults = []
        #checks to see if the two tickers appear in the default tickers
        for ticker in defaultTickers:
            #if the default ticker is not in the user's tickers
            if ticker not in uniqueTickers:  
                #if they are not the same, append to the possible list 
                possibleDefaults.append(ticker)
        #same as earlier, will just take the first possible default ticker
        #make sure to make the single default ticker back into list type to concatenate
        top3tickers = uniqueTickers + [possibleDefaults[0]]
    else: #the final case is if there are 3 or more unique tickers
        #we need to find how many times each ticker appears - their frequency
        tickerCounts = {}
        #make a dictionary with the ticker as a key and the values being their counts
        for ticker in tickers:
            if ticker in tickerCounts:
                tickerCounts[ticker] += 1
            else:
                tickerCounts[ticker] = 1

        #a dictionary of sorted tickers in reverse order, high to low
        #the key lambda parameter means that the dictionary is sorted in terms of each value
        #hence the x[1] that represents its sorted by the count / frequency
        sortedTickers = sorted(tickerCounts.items(), key=lambda x: x[1], reverse=True)

        top3tickers = []
        #loop through the sorted ticker tuples
        for tuple in sortedTickers[:3]:
            #append the first value from the tuple [0] which is the string ticker
            top3tickers.append(tuple[0])

    return top3tickers #return the top 3 tickers



#function definition used to create news records in table news with all relevant fields
def addNews(ticker, headline, sentiment, time, date):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = """ INSERT INTO tblNews (Ticker, Headline, Time, Date, Sentiment) 
                VALUES (?, ?, ?,?, ?)"""
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query, (ticker, headline, time, date, sentiment))
    connection.commit()

#function definition to extract data used to check if the same headline for the same ticker is 
#already in the database to prevent repetition of data 
def checkNews(ticker:str, headline:str):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = f""" SELECT tblNews.Ticker, tblNews.Headline
                 FROM tblNews
                 WHERE tblNews.Ticker = ? AND tblNews.Headline = ? """
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query, (ticker, headline))
    return cursor.fetchall()


#function definition to extract sentiments and headlines for a specific ticker for specific time ranges
#will be used to extract data to display on the gui
def extractNews(ticker,sentiment):
    #establish a connection between my code and my database
    #establish a cursor object to allow me to perform actions remotely on my database
    connection = sqlite3.connect("C:\\Users\\Ryan\\OneDrive - Cardinal Vaughan Memorial School\\NEA\\database.db")
    cursor = connection.cursor()
    query = f"""SELECT tblNews.Headline
                FROM tblNews
                WHERE tblNews.Ticker = ? AND tblNews.Sentiment = ? """
    #executes my sql query and retrieves all the rows as a result of the query
    cursor.execute(query, (ticker, sentiment))
    headlines = []
    #the headline is the first index of the tuple, since its the only thing I selected from each record
    for record in cursor.fetchall():
        headlines.append(record[0])
    return headlines

#function to validate password against security requirements
def validPass(password: str, username: str):
    #lsit of special characters
    specialChars = "!£$%^&*()_+-=''?><~@:}{[];#/.,"
    #True or False if there is a consecutive pattern of numbers or not
    consecutiveNum= bool(re.search(r"\d{3,}", password)) and any(
        str(i) + str(i + 1) + str(i + 2) or 
        str(i+2) + str(i+1) + str(i) in password for i in range(8))
    #returns false if password length not between 8 and 12
    if (len(password) < 8 ) or (len(password) > 12):
        return (False, "Not between 8 and 12 characters")
    #returns false if the username is in the password
    elif username in password:
        return (False, "Username cannot appear in password")
    #return false if there is no lowwer case letter, upper case letter or a digit  
    elif not(any(letter.islower() for letter in password) and 
             any(letter.isupper() for letter in password) and 
             any(letter.isdigit() for letter in password)):
        return (False, "Must have uppercase, lowercase and digit")
    #returns false if there is a consecutive series of numbers
    elif consecutiveNum == True:
        return (False, "Must not have consecutive numbers")
    #loops through the characters in the password and check if there is a special character
    for i in range(len(password)):
        if password[i] in specialChars:
            break #breaks the loop if a special character is found
        #if the loop is on the last character and there is no special character false will be returned
        elif i == len(password)-1:
            return (False, "Must have a special character")
    #if all that validation was smooth, then will consider going out 
    return (True, "Password valid")

#function to hash a password
def hashPass(password: str):
    #using the library to generate a one time salt
    salt = bcrypt.gensalt()
    #hash the passowrd using the salt to make it unique and harder to crack
    #this means even the same password will output a different hash
    hashed = bcrypt.hashpw(password.encode(), salt) 
    return hashed.decode()

#function to check that the password entered by user matches hashed one in database
def verifyPass(password: str, hashedPass: str) -> bool:
    #uses library function to automate the process
    return bcrypt.checkpw(password.encode(), hashedPass.encode())


createTables() #calls a function to create the tables



cursor.close()
connection.close()

