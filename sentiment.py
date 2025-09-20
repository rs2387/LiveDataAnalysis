#importing modules / libraries
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import math
#importing functions from my other file
from database import addNews, checkNews

#function definition to get headlines and the date / time of when each article was published 
def getHeadlines(tickers:list):

    #initialise empty lists to feed processed data into
    headlines, dates, times = [], [], []

    #loops through each ticker passed in the function
    for ticker in tickers:
        #adjusts the url for each ticker
        tickerURL = f"https://finance.yahoo.com/quote/{ticker}-USD/latest-news/"
        #set headers to stop the server rejecting my request or limiting the number of requests
        headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.google.com/",
                    "DNT": "1", 
                    "Connection": "keep-alive",
                    "Cache-Control": "no-cache",
                }

        #get the html and find all cases of the specific class that holds the headlines
        newsResponse = requests.get(tickerURL, headers=headers)
        newsSoup = BeautifulSoup(newsResponse.content,'html.parser')
        #I had to go on the website and inspect the html manually to find the class I wanted
        news = newsSoup.findAll('h3',class_='clamp yf-82qtw3')

        #do the same thing for the links for each headline - the only way I can access the date and time
        links = newsSoup.findAll('a', class_='subtle-link fin-size-small titles noUnderline yf-1xqzjha')
        #list comprehension to find all the href instances in the class
        newsURLS = [link["href"] for link in links] 

        #loops through each url in the list and requests each of those html soups
        #this had to be done because on the latest news page, the exact date time was not given,
        #so I had to basically "press" each headlines to go to the full article, request the html for the
        #full articles, and then extract the datetime object I wanted, all in this single loop
        for url in newsURLS:
                #request each articles full html soup
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content,'html.parser')
                #find the insance of the class holding the timestamp
                timeStamps = soup.findAll('time',class_='byline-attr-meta-time')

                #for each tag in the list given back, it holds a datetime object, which I converted
                #into python datetime, and then seperated into date and time seperately
                for tag in timeStamps:
                    stringObject =tag["datetime"]  
                    dateObject = datetime.strptime(stringObject, "%Y-%m-%dT%H:%M:%S.%fZ")
                    #append date part of datetime to a list
                    dates.append(dateObject.date())
                    #append time part of datetime to a list
                    times.append(dateObject.time())
                

        #each headline is returned in an unwanted format 
        #so I used string slicing to only take the exact part of the headline I need
        #without any of the surrouding class data
        for headline in news:
                #where the slice will begin
                startIndex = str(headline).find(">") + 1
                #where the slice will end
                endIndex = str(headline).rfind("<")
                #slice it and store as a string data type
                headline = str(headline)[startIndex:endIndex]  
                #if there in no headline, or it is repeated for some reason, do not append
                if headline in headlines:
                        pass
                elif headline == []:
                        pass
                #otherwise append to final list
                else:
                    headlines.append(headline)    
        
    #return each list
    return headlines, dates, times


#function definition that will return sentiments for each headline for any tickers
def sentiment(tickers:list):
    #these headlines were scraped using html parser, and recursively passed through external publicly available sentiment 
    #analysis models, as well as chat gpt's analysis and my own analysis to adjust certain headlines'' sentiment scores
    #that may have been produced. the program will then take these as training data to create a vocabulary dictionary
    #and to identify how many occurences of each word in a positive, negative or neutral setting
    trainingData = [
        ("Why corporate digital asset strategy can 'drive crypto market'", 0.732),
        ("One thing crypto must fix to become the currency of the future", 0.173),
        ("Trending tickers: GameStop, Palo Alto, Coinbase, Airbnb and Hermes", 0.857),
        ("FTSE and US stocks down as details emerge of Trump's reciprocal tariff plan", -0.738),
        ("Coinbase earnings: The factors that matter more than the Q4 beat", 0.254),
        ("Coinbase posts Q4 revenue beat, blows past earnings estimates", 0.921),
        ("Robinhood's Q4 crypto revenue soars 700% year-over-year", 0.982),
        ("The effect 'peer pressure' among financial advisors has on crypto", -0.667),
        ("Bitcoin Price Rises but XRP Slips. Why Crypto Investors Are on Edge.", 0.003),
        ("Trending tickers: Tesla, GameStop, Palantir, Super Micro Computer and Entain", 0.582),
        ("Is the UK government sitting on a bitcoin goldmine?", 0.854),
        ("GameStop, Lyft and Mobileye, T-Mobile: Market Minute", 0.000),
        ("XRP Falls, Bitcoin Rises. What the Latest Levies Mean for Crypto Prices.", 0.182),
        ("Donald Trump's DJT wants to get into the bitcoin ETF business", 0.257),
        ("You can now find bitcoin ATMs in some Costco stores", 0.753),
        ("XRP, Bitcoin Jump. Why the Jobs Report Is Driving Crypto.", 0.807),
        ("XRP Falls, Bitcoin Rises. Why the Crypto Fallout From Trump Tariffs Is Mixed.", -0.503),
        ("The most popular stocks and funds for investors in January", 0.000),
        ("MicroStrategy rebrands as Strategy, leaning further into its bitcoin commitment", 0.224),
        ("XRP Price Rises, But Bitcoin Falls. Why the Crypto Could Dive to $80,000.", -0.722),
        ("Ether Close to Three-month Lows", -0.757),
        ("XRP, Bitcoin Prices Slide. Why China's Trump Tariffs Standoff Is Hitting Cryptos.", -0.923),
        ("XRP, Bitcoin Plummet. Why Trump Tariffs Are Dragging Down Cryptos.", -0.943),
        ("Ether, Memecoins Plunge as Traders Dump Risk After Trump Tariffs", -0.932),
        ("XRP, Bitcoin Price Steadies as Gold Soars. What Trump Has to Do With It.", -0.374),
        ("Bitcoin price soars past $105,000 as the Fed says US banks can serve crypto clients", 0.941),
        ("XRP, Bitcoin Rise. Why Fed Rate Talk Matters for Cryptos.", 0.673),
        ("XRP and Bitcoin Rise. How the Fed Could Hurt Cryptos.", 0.000),
        ("3 'big changes' to know about the 2025 tax season", 0.000),
        ("Bitcoin Follows Tech Stocks Lower as New AI App Rattles Markets", -0.553),
        ("XRP, Bitcoin Are Falling. It Isn't Just China's AI Threat That Is Hurting Crypto.", -0.653),
        ("Why Solana could be the big winner of the meme-coin frenzy", 0.583),
        ("XRP, Bitcoin Price Gains Stall. What Trump Actually Means for Crypto.", -0.631),
        ("Coinbase revenue spikes as crypto undergoes 'seismic shift'", 0.573),
        ("4 crypto pros sound off on Trump's executive order", -0.274),
        ("6 factors that could make or break crypto in 2025: Citi", 0.000),
        ("Rumble jumps after $775M Tether deal, boosting liquidity", 0.494),
        ("Eli Lilly, Qualcomm, Rumble: Market Minute", 0.000),
        ("Bitcoin rally lifts Solana, Coinbase, and other crypto plays", 0.624),
        ("XRP rallies as bitcoin and other top cryptocurrencies fall", 0.057),
        ("The crypto investors who could land inside Trump's White House", 0.000),
        ("Bitcoin rises amid crypto market rebound but ethereum outperforms", 0.563),
        ("Trump Picks Pro-Crypto Hedge Fund Manager Scott Bessent for Treasury Secretary", 0.000),
        ("Kraken, Tether-Backed Dutch Firm Rolls Out MiCA-Compliant Euro, U.S. Dollar Stablecoins", 0.663),
        ("Tether Unveils New Platform to Simplify Asset Tokenization for Businesses, Nation-States", 0.543),
        ("Money Launderer Who Moved Scam Victims' Funds Faces Up to Two Decades in U.S. Prison", -0.882),
        ("Stablecoin Giant Tether Enters Oil Trade by Financing $45M Middle Eastern Crude Deal", 0.691),
        ("Chinese Nationals Gain Access to Stablecoins in Hong Kong Via New Trial", 0.000),
        ("CEO of Canadian Crypto Holding Returns Safely After Paying $720K Ransom: Report", 0.000),
        ("Tether Reports $2.5B Profit in Q3, Holds Over $100B of U.S. Treasuries", 0.682),
        ("Crypto Rally Foiled by Report of DOJ Probe of Tether", -0.473),
        ("Bitcoin price recovers slightly ahead of Trump-Putin talks", 0.123),
        ("Elon Musk's record $447 billion fortune means he's nearly $200 billion ahead of Jeff Bezos — and worth more than Costco", 0.461),
        ("Crypto-linked stocks jump as bitcoin tops key $100,000 threshold for the first time ever", 0.562),
        ("XRP, DOGE Lead Crypto Losses as Weekend Pullback in Bitcoin Causes $500M Liquidations", -0.813),
        ("Memecoin Launchpad GraFun Expands to Ethereum to Clinch New Users", 0.523),
        ("Bitcoin hits fresh record near $85,000 as investors keep cheering 'crypto president' Trump", 0.682),
        ("As bitcoin hits record high, crypto traders 'confident' on Trump promises", 0.752),
        ("Bitcoin Surges Above $71K as Wild Crypto Market Pump Sees $175M in Shorts Liquidated", 0.593),
        ("Bitcoin Trader Warns of Correction as BTC Dominance Reaches 2021 Levels; Solana Leads Market Gains", 0.000),
        ("Bitcoin, Majors Dip on Leverage Flush; CAT Token Runs Up 60% on Binance Futures Listing", -0.421),
        ("GraFun Starts Labs Division to Boost Memecoin Ecosystem on BNB Chain", 0.553),
        ("Scroll Airdrop Allocation Met With Dismay From Farmers", -0.392),
        ("Bitcoin, Ether Nurse Losses as Dollar Strengthens Ahead of U.S. Inflation Report", -0.333),
        ("Crypto Majors BTC, ETH, XRP Little Changed as HBO Calls Peter Todd the Bitcoin Creator", 0.000),
        ("Bitcoin Poor Start to Bullish October Continues, but There May Be Cheer Ahead for Bulls", 0.163),
        ("GraFun, Supported by Floki and DWF Labs, Brings Memecoin Frenzy to BNB Chain", 0.624),
        ("Bitcoin Strength Continues on U.S, China Easing; Floki Bot Crosses Trading Milestone", 0.482),
        ("Bitcoin Holds Above $60K as Traders Warn of Sell-Off on 50 Basis Point Fed Rate Cut", 0.000),
        ("SEC Places Heavier Scrutiny on Binance's Token Listing, Trading Process in Proposed Amended Complaint", -0.521),
        ("XRP, DOGE Lead Market Gains as Bitcoin Dips Under $58K", 0.057),
        ("Bitcoin price rises amid ETF momentum and anticipation of Trump policies", 0.573),
        ("Bitcoin Slides Near $94K, but Short-Term Bullish Target of $100K BTC Unchanged", 0.000),
        ("ADA Gains 10.1% as Index Continues Higher", 0.463),
        ("Crypto rally will become a crypto rout if Trump doesn't deliver", -0.663),
        ("ADA Surges 18.4%, Leading Index Higher", 0.653),
        ("LTC Gains 8.5%, Leading Index Higher from Wednesday", 0.543),
        ("Cardano Foundation Spent $23.7M in 2023: Financial Insights Report", 0.000),
        ("CoinDesk 20 Performance Update: POL Declines 7.7%, Leading Index Lower", -0.481),
        ("Cardano's ADA Rockets 35% as Hoskinson Says He's Helping U.S. Crypto Policy", 0.632),
        ("ADA Gains 9.9%, Leading Index Higher from Thursday", 0.621),
        ("Bitcoin Pulls Under $68K as Crypto Markets Falter Ahead of Election", -0.623),
        ("APT Falls 4%, Leading Index Lower From Wednesday", -0.431),
        ("UNI Gains 6.3% as Nearly All Index Constituents Trade Higher", 0.553),
        ("Bitcoin Gains 5% to $61K Ahead of Fed, but Order Books Suggest Rally Could Be Capped", 0.232),
        ("What Trump did that 'embarrassed' the crypto community", -0.731),
        ("SEC task force stokes new crypto optimism as industry awaits Trump actions", 0.000),
        ("Inauguration 2025: Bitcoin hits record $109K, Trump launches memecoin", 0.721),
        ("Bitcoin price nears $100,000 ahead of Trump inauguration as US inflation cools", 0.581),
        ("Why the momentum driving bitcoin adoption is just getting started", 0.593),
        ("Why do people own bitcoin? An expert explains.", 0.000),
        ("Bitcoin prices could re-ignite in 2025 from DeFi uses, Trump admin", 0.463),
        ("Trump policy could bring 'enormous vindication' for crypto: Expert", 0.431),
        ("Bitcoin price rebounds above $100,000 as Fed could cut interest rates", 0.653),
        ("What SEC Chair Gary Gensler's resignation means for crypto", 0.173),
        ("Invest in crypto portfolios, not predictions: Bitwise CEO", 0.000),
        ("Strategic bitcoin reserve should top Trump's to-do list: Pompliano", 0.000),
        ("Bitcoin could hit $100K under Trump: Asymmetric CEO", 0.441),
        ("Bitcoin surges to record high of $81k after Trump wins US election", 0.673),
        ("Be careful what you wish for on crypto regulation, this bear says", -0.674),
        ("XRP Price Rises. 2 Things That Could Decide the Crypto's Future Under Trump.", 0.203),
        ("5 things to know about Trump's meme-coin frenzy", -0.493),
        ("Tariff dip, February markets, bitcoin jumps: Market Takeaways", 0.000),
        ("Coinbase CEO Brian Armstrong says there are 1 million new cryptocurrencies created every week", 0.000),
        ("Trump's embrace of meme coin sours mood in crypto industry", -0.544),
        ("Trump inauguration fuels bitcoin and memecoin rally", 0.592),
        ("Donald and Melania Trump launch cryptocurrency meme coins before inauguration", 0.000),
        ("The Grinch loves knee surgery. That's it. That's the meme.", 0.182),
        ("Eddie Johnson's 5% Rule for crypto investing", 0.000),
        ("4 things to know about Trump Media's move to buy an unprofitable crypto platform", -0.444),
        ("USDC issuer Circle plans US move ahead of IPO", 0.573),
        ("Stripe reopens crypto payments with USDC focus", 0.000),
        ("Binance converts US$1 bln fund; eyes India comeback after obtaining Dubai license", 0.511),
        ("The 3 Best Stablecoins for Beginning Crypto Investors", 0.293),
        ("The 10 biggest cryptocurrencies in a market that's now worth almost $3 trillion", 0.000),
        ("Top 3 Stablecoins to Watch in 2024: A Beginner's Guide to Crypto Stability", 0.000),
        ("Circle ends USDC support on TRON network", -0.261),
        ("Crypto needs open-minded regulators: BitGo CEO", 0.000),
        ("NEAR Gains 4.8% as Almost All Assets Trade Higher", 0.511),
        ("LINK Falls 5.7% as Nearly All Index Constituents Decline", -0.261),
        ("LINK and ICP Gain 3.8% as Index Trades Higher From Thursday", 0.511),
        ("HBAR Drops 5.1% as Index Trades Lower From Wednesday", -0.361),
        ("LTC Gains 3%, Leading Index Higher", 0.413),
        ("Ex-Valkyrie Founder's Canary Capital Group Files for First Litecoin ETF", 0.533),
        ("Index Drops 1.2%, With NEAR and RENDER Posting Biggest Declines", -0.323),
        ("AVAX Gains 3.6% as Index Rallies", 0.441),
        ("NEAR Leaps 6.3% as All Assets Rise", 0.523),
        ("ICP Gains 4.4%, Leading Index Higher", 0.471),
        ("Index Surges 5.3% With All Assets in the Green", 0.492),
        ("UNI Drops 4.7%, Leading Index Lower", -0.283),
        ("AVAX Surges 12.8%, Pushing Index Higher", 0.761),
        ("Heavy Losses in APT and MATIC Lead the Index Lower", -0.731),
        ("MATIC Plunges 6.9%, Leading Index's Decline", -0.641),
        ("LTC and BCH Lead as Index Gains 0.4%", 0.454),
        ("UNI Gains 5% as Index Rises from Thursday", 0.423),
        ("BCH Drops 4.3% as Index Declines from Tuesday", -0.314),
        ("APT Falls 2.7%, Leading Index Lower", -0.521),
        ("ICP Drops 3.5% as Index Inches Lower From Monday", -0.493),
        ("APT Drops 2.4%, Leading Index Lower", -0.331),
        ("LINK Surges by 7.1% as Index Rises", 0.572),
        ("ICP and RNDR Each Drop 3.6%, Leading Index Lower", -0.273),
        ("Index Tumbles 3.2%, With RNDR the Only Asset to Advance", -0.283),
        ("RNDR Surges 6.9% as Index Inches Higher", 0.431),
        ("Bitcoin Flipflops; MATIC, LINK Surge as Dim Market Action Continues", 0.000),
        ("ICP and RNDR Lead Losses as Index Slips 2.2%", -0.273),
        ("19 Out of 20 Assets in the Green", 0.482),
        ("Bitcoin Pullback to $66K Triggers $250M in Crypto Liquidations as Traders Brace for 'Wild Wednesday' of FOMC, CPI Report", -0.354),
        ("Young Money: 4 Cryptos Perfect for Millennial and Gen-Z Investors", 0.503),
        ("SHIB's 106% Move Higher Led CoinDesk 20 Gainers Last Week: CoinDesk Indices Market Update", 0.831),
        ("Meme Coins DOGE and SHIB Led CoinDesk 20 Gainers Last Week: CoinDesk Indices Charts", 0.651),
        ("Protocol Village: Layer-2 Network Metis Integrates Chainlink CCIP as Canonical Token Bridge", 0.571),
        ("BCH Gains 13.1%, Leading Index Higher from Wednesday", 0.603),
        ("BCH and SOL Gains Lead as Index Inches Up 0.3%", 0.471),
        ("XRP's 7.8% Decline Weighs on Index", -0.357),
        ("SOL Leads with 3.9% Gain as Index Rebounds", 0.441),
        ("Index Gains 1.2% With BCH and ETC Leading", 0.421),
        ("XRP and SOL Outperform as Index Climbs 1.3%", 0.362),
        ("BCH's 21% Surge Leads Index Gain", 0.684),
        ("Bitcoin Nears $70K on Back of Trump's Speech, Bitcoin Cash and Base Memecoins Lead Crypto Market Gains", -0.392),
        ("Mixed Results with XRP and ICP Leading", 0.000),
        ("Bitcoin Cash's Mt. Gox-Led Sell-Off Is Amplified by Poor Liquidity", -0.371),
        ("NEAR and AVAX Lead", 0.541),
        ("XRP, LINK, ETH Stand Out Relative to BTC in Sector Rotation Analysis, DOGE Struggles", 0.523),
        ("Bitcoin Cash Spikes 10% After Halving, Bitcoin Hovers Above $66K", 0.482),
        ("Buy the Dip! 3 Cryptos to Buy Before Bitcoin's Next Leg Up.", 0.563),
        ("Koreans Go Full Monty on DOGE, XRP, XLM After Trump's Win; Now Look to SAND Token", 0.000),
        ("XLM Surges 73.2% Over Weekend in Broad Rally", 0.864),
        ("Uniswap Surges 28% as All Index Constituents Trade Higher After Election", 0.639),
        ("Protocol Village: Degen Community, Syndicate Launch 'Degen Chain'", 0.553),
        ("The Blockchain Industry Must Build for the Real Needs of Real People", 0.684),
        ("Stellar Starts Phased Rollout of 'Soroban' Smart Contracts", 0.591),
        ("Top 3 Exchange Cryptos to Buy Before Volumes Soar", 0.571),
        ("3 Hot Cryptos to Buy if You Only Have $100", 0.453),
        ("Falls 5.7% as Nearly All Index Constituents Decline", -0.901),
        ("Caution: 3 Meme Coins on the Verge of a Major Collapse", -0.581),
        ("Could altcoins be the new winners in cooling crypto rally?", 0.000),
        ("3 High-Growth Cryptos That Have Major Catalysts Ahead", 0.543),
        ("Pre-Bitcoin Halving Special: 3 Cryptos to Buy Before They Go Parabolic", 0.653),
        ("Beyond ETH: 3 Cryptos That Are a Better Bet Than Ethereum", 0.532),
        ("3 Meme Coins to Sell in July Before They Crash & Burn", -0.702),
        ("Bitcoin has tipped into a bear market, slipping 23% from previous highs", -0.862),
        ("3 Cryptocurrencies to Buy as U.S. Debt Continues to Grow", 0.000),
        ("3 Meme Coins to Sell in June Before They Dive", -0.602),
        ("Why Meme Coins Baby Dogecoin, Shiba Inu and Smog Are Headed for Disaster", -0.743),
        ("Crypto just became a political football, and ether is the early winner", 0.591),
        ("3 Cryptos You've Never Heard Of (But Will Want to Buy Immediately)", 0.463),
        ("Crypto Carnage Ahead? 3 Tokens to Dump Before the Bloodbath", -0.523),
        ("Meme Coin Meltdown: 3 Volatile Tokens to Dump Now", -0.523),
        ("Short-Term Bets: 3 Cryptos to Buy BEFORE the Bitcoin Halving", 0.471),
        ("3 Amazing Altcoins That Can Double by The Bitcoin Halving", 0.482),
        ("3 Cryptos That You'll Wish You Bought Instead of Shiba Inu", 0.482),
        ("Don't Get Burned: Sell These 3 High-Risk Cryptos Before It's Too Late", -0.533),
        ("Crypto meme tokens like 'dogwifhat' and 'Baby Doge Coin' are booming as bitcoin surges", 0.523),
        ("3 Meme Coins to Sell in March Before They Crash & Burn", -0.523),
        ("Wanna Be a Future Crypto Millionaire? Invest in POL, VET and BTC.", 0.543),
        ("3 Cryptos Primed for 50X Gains Once Bitcoin Crosses $100,000", 0.551),
        ("7 Cryptos to Buy on the Dip Before They Mint Fortunes", 0.463),
        ("SEC dropping Coinbase lawsuit is 'monumental' for crypto", 0.937),
        ("lost liquidation may have lost over $16 billion in early liquidation of bitcoins", -0.912),
        ("The Weekend: When Europe's do-or-die moment sent defence stocks soaring", 0.825),
        ("crash plummeting decline loss lost drop falling tank crater collapsed slump downturn", -0.999),
        ("collapse downward broke failure weakness pessimistic dropinvalue depreciation", -0.999),
        ("negative losses sink worsening stagnant unfavorable crashdown hardhit unpredictable", -0.999),
        ("unsustainable plunge bottomout low falloff unravel downtrend unprofitable unsettling", -0.999),
        ("downwardspiral reversal descent overleveraged unsupportable panic bearmarket", -0.999),
        ("shortsell liquidation uncertainty scam manipulation dump exploit recession dive", -0.999),
        ("strife bankrupt insolvency fears marketcorrection sinking bloodbath devastating", -0.999),
        ("rise soar boom upward surge gain spike record prosperity positive advance", 0.999),
        ("success opportunity thriving explosion uptick accelerate profits shining optimistic", 0.999),
        ("rebounds optimism highs growth flourish promising skyrocket leadership investment", 0.999),
        ("exceeding strengthen powerful explosive uptrend robust secure valued support", 0.999),
        ("fortunes breakout momentum exciting high profit thriving trending stellar return", 0.999),
        ("excellent steady recordbreaking attracting boost expansion improvement breakthrough", 0.999),
    ]


    #initilaise empty lists to seperate out the training data
    trainingVectors, trainingLabels, trainingHeadlines = [], [], []

    #initialise a list of determiners and filler words to remove
    determiners = ["i","coinbase","is","may", "have", "says","cryto", "ticker", "tickers", "this",
                    "the", "a", "an","on", "as", "and", "to", "of", "it", "in", "from","because", "at",
                    "than", "that", "has", 'CoinDesk', "Performance", "Update"]

    #open a file path, this is needed to allow the vocab list to save when the training data changes 
    #even if I delete or change or add training data, the old vocab list will not be removed, the new vocab
    #will just be sort of 'appened' to the end of it using csv files to store it
    filePath = 'vocabTraining.csv'

    #calls a function to get all the headlines, dates and times for a given ticker
    headlines, dates, times = getHeadlines(tickers)

    #function definition that will take a headline as input and return a list of words
    def preprocess(headline:str):
        words = ""
        for char in headline.lower():
            #removes all characters except for alphanumerics and spaces
            if char.isalnum() or char.isspace():
                words = words + char
        words = words.split(' ')
        finalList = []
        for word in words:
            #checks to see if each word is in determiners, if not 
            #added to the final list of words
            if word not in determiners:
                #removes common suffixes to try stop repeat instances of different variations of the root
                suffixes = ['ings', 'ing', 'ed', 's', 'ly', 'est'] #list of common suffixes
                vowels = "eiouya" #string of vowels
                #removes common suffixes to try stop repeat instances of different variations of the root
                for suffix in suffixes: #loop through each suffix
                    appended= False
                    if word.endswith(suffix): #check if the word ends with it
                        if suffix == "s" and word[-2]=="s": #if it ends with an s with another s before it
                            break #end the for loop and change nothing
                        #if it ends with an ing with a vowel two letter before the ing 
                        elif (suffix == "ing" and word[-5] in vowels[1:]) or (suffix == "ed" and len(word) > 4 and word[-4] in vowels[1:]):
                            finalList.append(word.removesuffix(suffix)+"e") #remove suffix and add e
                            appended = True #set appended to true
                            break #end the for loop
                        finalList.append(word.removesuffix(suffix))
                        appended = True
                        break
                else:
                    if not appended: #if it didnt match any of the suffixes then append to the list
                        finalList.append(word)
        return finalList #returns a processed list of words

    #function definition that will take headline as input and return dictionary
    #of words, each word is a unique key with a unique numerical value
    def buildVocabulary(headlines):
        #initialise empty dictionary
        vocab = {}
        index = 0
        for headline in headlines:
            #calls a function I made to split the headline into a list of words
            words = preprocess(headline)

            #if the word is not in the dictionary already,
            #it is added as a key, with its value increasing with index
            for word in words:
                if word not in vocab:
                    vocab[word] = index
                    index += 1
        
        return vocab 

    
    #function definition, takes two dictionaries as parameters
    def addVocab(dict1: dict, dict2:dict):
        #opens the csv file in write mode
        with open(filePath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            #if dict2 is empty, I just write dict1 into the csv
            if dict2 == {} or dict2== None:
                for key, value in (dict1).items():                              
                    writer.writerow([key, value])
            #otherwise, add dict2 to dict1 without duplicates
            elif dict2 != {} and dict2 != None:
                dict1.update(dict2) 
                count = 0
                #count makes sure each values for each key is unique number
                for key, value in (dict1).items():
                    writer.writerow([key, count])
                    count += 1

    #initialise empty dictionary for vocab from previous running of program
    oldVocab = {}

    #function definition that reads existing csv file, and rewrites the data
    #into a dicionary
    def getVocab():
        try:
            with open(filePath, mode="r") as csvfile:
                reader = csv.reader(csvfile)
                #loop through each row and store in the old vocab dict
                for row in reader:
                    if row:  
                        key, value = row
                        oldVocab[key] = value 
                return oldVocab
        except: #if the file path doesn't exist, I just create the file
            open(filePath, 'w', newline='')

        
    #function definition to make each headline into a vector
    def makeVector(headline):
        vocab = getVocab() #dictionary of existing vocab
        words = preprocess(headline) #makes headline into list of words
        vector = [0] * len(vocab) #makes the vector as long as the number of words in vocab
        #each index of the vector corresponds to a word from vocab, each time a word from 
        #the headlines appears, its corresponding index value in the vector increases by 1
        for word in words:
            if word in vocab:
                vector[int(vocab[word])] += 1
        
        return vector 
    

    #function definition to fill in previously initialised lists
    def initialiseTrainingParameters(trainingData):
        for data in trainingData:
            #each headline string will be used to build the vocabulary
            trainingHeadlines.append(data[0])
            #each headlines sentiment appended to labels
            trainingLabels.append(data[1])
    
    #calls the function
    initialiseTrainingParameters(trainingData)
    

    #calls the function build vocab using the training headlines as data
    vocab = buildVocabulary(trainingHeadlines)

    #if there is already vocabulary stored in the csv, 
    #the call to getVocab will return a dictionary otherwise it will make a new file
    oldVocab = getVocab()
  
    #calls add vocab function with dict1 and dict2 as parameters
    #if there is old vocab in the csv, dict2 will not be {}, so dict1
    #will be updates and the vocabulary is combined
    addVocab(vocab, oldVocab)
    oldVocab = vocab #set the value of old vocab to vocab since its now been updated

    #loop through each training headline  
    for data in trainingData:
            #each headline made into vector, can only be done after the all the vocab has been sorted out
            trainingVectors.append(makeVector(data[0]))



        # - trainingVectors is a list of vectors that each represent a headline in the same format
        # that the makeVector function returns
        # - lables is a list of equal size of that of the trainingVectors list that corresponds to
        # each singular training vector in that list, with either a 1 or a 0 labelling it as positive
        # or negative respectively
        # - the size of my vocabulary is needed to map other lists, positive word counts and negative
        # word counts to the same length as the original vectors
        # - I initialise the total number of positive and negative words as 0 - these values will be
        # needed when we want to calculate the probability of a word being positive or negative as
        # well as the number of times each word appears in a positive or negative headline
        # - I use a for loop to iterate over all the training vectors in the list, and if its
        # corresponding label is close to 1 (which is strong positive) so about greater than 0.2,
        # I add the total number of words within that training vector to the total positive words,
        # and a little less for the negative ones.
        # - Then I use a second for loop to go through each term in the training vector and copy it
        # into the positive or negative count for that specific word which is the number of times
        # that word appears in a positive or negative headline
        # - Finally I plug the values into the probability formula, lots of youtube videos helped
        # me learn about it and it is based on a Naive Bayes classifier. The reason for adding 1.5
        # is in case that the words aren't in the vocab, it prevents a probability of 0 which
        # would be wrong. This is called Laplace smoothing.

    def trainSentimentAnalysis(trainingVectors, labels):
        #the number of different words in my vocabulary
        vocabSize = len(getVocab())

        #initialise lists to hold count of each word in a positive or negative sentence
        positiveCounts =[0] * vocabSize
        negativeCounts = [0] * vocabSize
  
        #the total number of words counted in a positive and negative sentence
        totalPositiveWords, totalNegativeWords = 0, 0

        #goes through each training headline in vector format
        for i in range(len(trainingVectors)):
            #if the sentiment is greater than 0.2 is it seen as positive
            if labels[i] > 0.3:  
                totalPositiveWords += sum(trainingVectors[i])
                for j in range(vocabSize):
                    positiveCounts[j] += trainingVectors[i][j]
            #if the sentiment is less than -0.2 is it seen as negative
            elif labels[i] < -0.3: 
                totalNegativeWords += sum(trainingVectors[i])
                for j in range(vocabSize):
                    negativeCounts[j] += trainingVectors[i][j]


        #calculate the probabilities for each word being in a positive or negative sentence
        #using Laplace smoothing, I add 1 to each count so no probabilities are 0
        smoothing = 1
        positiveProbabilityForEachWord, negativeProbabilityForEachWord = [], []

        
        #loop through all of vocab to calculate the probability for each word being positve or negative
        for k in range(vocabSize):
            #using a probability formula
            #the probabily of the word the word being positive is the number of times that word appeared in a 
            #positive setting divided by the total number of positive words plsplus the number of words in vocab 
            #I decided to divide the Vocab size by 1.5 since I felt there were too many words that don't appear much
            positiveProbabilityForEachWord.append((positiveCounts[k] + smoothing) / (totalPositiveWords + vocabSize/1.5))
            negativeProbabilityForEachWord.append((negativeCounts[k] + smoothing) / (totalNegativeWords + vocabSize/1.5))


        return positiveProbabilityForEachWord, negativeProbabilityForEachWord


    #call on training function to find probility of each word being positive or negative
    positiveProbabilityForEachWord, negativeProbabilityForEachWord = trainSentimentAnalysis(trainingVectors, trainingLabels)

    #function definition for hyperbolic tangent(x)
    def tanh(x):
        exponential = math.exp(x)
        negativeExponential = math.exp(-x)
        return (exponential - negativeExponential) / (exponential + negativeExponential)


    #function definition to predict sentiment
    def predict(headline, positiveProbabilityForEachWord, negativeProbabilityForEachWord):
        #converts headline into vector
        vector = makeVector(headline) 


        #at this point headline has a vector of length vocab, with each index of the vector
        #matching to a word in vocab, and each value in vector references the number of times
        #that word has appeared
        #in the same manner, the negative and positive probabilities are of length vocab and 
        #each index maps onto a word in vocab and each value is the probability of that word
        #having negative or positive connotations
        
        #intialises probabilities as 0
        logPositive, logNegative = 0, 0

        #loop through each index of the vector which represents a word in vocab
        for i in range(len(vector)):
            if vector[i] > 0: #if that word appears in the headline
                #each word has a given negative and positive probability and that is
                #multiplied by the number of times the word appears and appended to the 
                #total positive and negative probabilities
                logPositive += math.log(positiveProbabilityForEachWord[i]) * vector[i]
                logNegative += math.log(negativeProbabilityForEachWord[i]) * vector[i]

        #probability of headline being positive subtract that of it being negative
        score = logPositive - logNegative

        #call on tanh function to better map the values between 1 and -1 
        #also acts as a smoothing function for the range of scores
        sentiment = tanh(score/4)

        return sentiment
    
    
    #initialise empty list for sentiments
    sentiments = []
    #loops through each headline and append its sentiment score to the list
    for i in range(len(headlines)):
        #call on the predict function
        sentiments.append(predict(headlines[i], positiveProbabilityForEachWord, negativeProbabilityForEachWord))
    return headlines, sentiments, dates, times



def recent10(tickers:list):
    #loops through list of tickers
    for ticker in tickers:
        #initialise total as empty list and scores as 0
        total, scores = [], 0
        #for each ticker, get all the headlines, sentiments, dates and times
        headlines, sentiments, dates, times = sentiment([ticker])
        #for each headline, if the sentiment is more than 
        for i in range(len(headlines)):
            #selection statement to split the numerical values into 3 categories
            if sentiments[i] > 0.15:
                sentimentScore = "Positive"
            elif sentiments[i] < -0.15:
                sentimentScore = "Negative"
            else:
                sentimentScore = "Neutral"
            #try to create a record in table News
            if len(total) < 10:
                scores += sentiments[i]
                total.append(f"{headlines[i]}: {sentimentScore}, {sentiments[i]}")

            try:
                #calls a function to chech if there is a record with the same ticker and headline as the
                #one that I will add next
                if checkNews(ticker+"USDT", headlines[i]) == []:
                    #calls a function to add the headlines to the database
                    addNews(ticker=ticker+"USDT", headline=headlines[i], time=f"{times[i]}", date=f"{dates[i]}", sentiment=sentimentScore)
                else: #otherwise raise an exception
                    raise Exception
            #the exception will be raised if the same ticker and headline is trying to be added
            except Exception as e:
                pass

        return total, scores
    
