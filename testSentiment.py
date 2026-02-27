from datetime import date, time
from sentiment import sentiment

def getMockHeadlines():
    mock_data = [
        #ai generated positive headlines
        ("Bitcoin surges past $95,000 as institutional demand hits record highs", date(2025, 2, 20), time(9, 30, 0), "positive"),
        ("Coinbase stock jumps 12% after beating Q1 revenue estimates", date(2025, 2, 20), time(10, 15, 0), "positive"),
        ("XRP, Solana Lead Gains as Crypto Market Rebounds Strongly", date(2025, 2, 19), time(14, 0, 0), "positive"),
        ("Bitcoin ETF sees record $500M inflows in single day", date(2025, 2, 19), time(11, 45, 0), "positive"),
        ("SOL Surges 18.3%, Leading Index to Best Week of 2025", date(2025, 2, 18), time(8, 0, 0), "positive"),
        ("Bitcoin Tops $100K for Second Time as Wall Street Demand Grows", date(2025, 2, 21), time(9, 0, 0), "positive"),
        ("Robinhood Crypto Revenue Doubles Year-Over-Year, Stock Surges", date(2025, 2, 21), time(9, 30, 0), "positive"),
        ("AVAX Surges 14.2%, Leading Index to Weekly Highs", date(2025, 2, 21), time(10, 0, 0), "positive"),
        ("MicroStrategy Adds 10,000 Bitcoin to Treasury, Stock Jumps 8%", date(2025, 2, 21), time(10, 30, 0), "positive"),
        ("XRP Gains 11.3% as Court Rules in Ripple's Favor", date(2025, 2, 21), time(11, 0, 0), "positive"),
        ("Crypto market cap hits $3.5 trillion as bitcoin leads rally", date(2025, 2, 21), time(11, 30, 0), "positive"),
        ("LINK Surges 9.4% as Index Posts Best Day in Three Months", date(2025, 2, 21), time(12, 0, 0), "positive"),
        ("Cardano's ADA Jumps 22% After Major Protocol Upgrade", date(2025, 2, 21), time(12, 30, 0), "positive"),
        ("Bitcoin price rebounds above $97,000 as Fed signals rate pause", date(2025, 2, 21), time(13, 0, 0), "positive"),
        ("SOL, AVAX Lead as 19 Out of 20 Index Assets Trade Higher", date(2025, 2, 21), time(13, 30, 0), "positive"),
        ("Ethereum ETF inflows hit $300M, pushing ETH above $3,500", date(2025, 2, 21), time(14, 0, 0), "positive"),
        ("LTC Gains 7.8%, Leading Index Higher From Tuesday", date(2025, 2, 21), time(14, 30, 0), "positive"),
        ("Coinbase added to S&P 500, shares spike 15%", date(2025, 2, 21), time(15, 0, 0), "positive"),
        ("Bitcoin hits fresh all-time high as Trump signs crypto executive order", date(2025, 2, 21), time(15, 30, 0), "positive"),
        ("Index Surges 6.1% With All 20 Assets in the Green", date(2025, 2, 21), time(16, 0, 0), "positive"),

        #ai generated negative headlines
        ("Bitcoin Plunges Below $80,000 as Tariff Fears Grip Markets", date(2025, 2, 20), time(16, 0, 0), "negative"),
        ("XRP, DOGE Lead Losses as Crypto Selloff Wipes $200B From Market", date(2025, 2, 20), time(12, 30, 0), "negative"),
        ("Ether Slides to Four-Month Lows Amid Broad Market Weakness", date(2025, 2, 19), time(9, 0, 0), "negative"),
        ("SEC Expands Probe Into Binance Token Listings, Stocks Drop", date(2025, 2, 18), time(17, 30, 0), "negative"),
        ("Bitcoin, Majors Tumble as Inflation Data Rattles Risk Assets", date(2025, 2, 17), time(15, 0, 0), "negative"),
        ("Bitcoin Crashes Below $75,000 Triggering $800M in Liquidations", date(2025, 2, 22), time(9, 0, 0), "negative"),
        ("XRP, SOL Plunge as Trump Tariff Escalation Hammers Risk Assets", date(2025, 2, 22), time(9, 30, 0), "negative"),
        ("MATIC Drops 11.2%, Leading Index to Worst Session of the Month", date(2025, 2, 22), time(10, 0, 0), "negative"),
        ("Ether falls to five-month lows as whale selloff accelerates", date(2025, 2, 22), time(10, 30, 0), "negative"),
        ("Binance faces fresh DOJ scrutiny, BNB slides 9%", date(2025, 2, 22), time(11, 0, 0), "negative"),
        ("Crypto Carnage: $400B wiped from market as recession fears mount", date(2025, 2, 22), time(11, 30, 0), "negative"),
        ("APT Plunges 13.5% as Index Posts Worst Week Since 2024", date(2025, 2, 22), time(12, 0, 0), "negative"),
        ("Bitcoin bear market fears grow as price slips 25% from peak", date(2025, 2, 22), time(12, 30, 0), "negative"),
        ("Meme coins DOGE, SHIB collapse as retail investors flee crypto", date(2025, 2, 22), time(13, 0, 0), "negative"),
        ("Heavy Losses in SOL and AVAX Drag Index Down 7.3%", date(2025, 2, 22), time(13, 30, 0), "negative"),
        ("SEC sues major DeFi protocol, tokens across sector tumble", date(2025, 2, 22), time(14, 0, 0), "negative"),
        ("ICP Drops 8.9% as Index Declines for Fourth Straight Day", date(2025, 2, 22), time(14, 30, 0), "negative"),
        ("Bitcoin Follows Nasdaq Lower as Rate Hike Fears Rattle Markets", date(2025, 2, 22), time(15, 0, 0), "negative"),
        ("Crypto exchange hack exposes $200M in user funds", date(2025, 2, 22), time(15, 30, 0), "negative"),
        ("XRP, DOGE, SHIB All Fall Over 10% in Weekend Bloodbath", date(2025, 2, 22), time(16, 0, 0), "negative"),

        #ai generated neutral headlines
        ("What Trump's latest executive order actually means for crypto", date(2025, 2, 20), time(13, 0, 0), "neutral"),
        ("Trending tickers: Coinbase, MicroStrategy, Ripple and Marathon Digital", date(2025, 2, 19), time(10, 0, 0), "neutral"),
        ("3 things to know about the proposed US strategic bitcoin reserve", date(2025, 2, 18), time(9, 30, 0), "neutral"),
        ("Why do institutions keep buying bitcoin? An expert explains.", date(2025, 2, 17), time(11, 0, 0), "neutral"),
        ("Bitcoin, Ether Little Changed as Markets Await Fed Decision", date(2025, 2, 16), time(8, 30, 0), "neutral"),
        ("Bitcoin price holds near $88,000 ahead of key inflation report", date(2025, 2, 23), time(9, 0, 0), "neutral"),
        ("6 things to know about the SEC's new crypto task force", date(2025, 2, 23), time(9, 30, 0), "neutral"),
        ("Trending tickers: Bitcoin, Ethereum, Solana, Cardano and Ripple", date(2025, 2, 23), time(10, 0, 0), "neutral"),
        ("What Elon Musk's latest comments actually mean for Dogecoin", date(2025, 2, 23), time(10, 30, 0), "neutral"),
        ("Mixed Results: XRP and LTC Gain While ETH and SOL Slip", date(2025, 2, 23), time(11, 0, 0), "neutral"),
        ("Crypto market flat as investors weigh Fed minutes, jobs data", date(2025, 2, 23), time(11, 30, 0), "neutral"),
        ("Is bitcoin a hedge against inflation? Experts are divided.", date(2025, 2, 23), time(12, 0, 0), "neutral"),
        ("Coinbase CEO says crypto regulation clarity could take years", date(2025, 2, 23), time(12, 30, 0), "neutral"),
        ("Bitcoin, Majors Little Changed as Traders Await Powell Speech", date(2025, 2, 23), time(13, 0, 0), "neutral"),
        ("5 factors that will shape the crypto market in Q2 2025", date(2025, 2, 23), time(13, 30, 0), "neutral"),
        ("Tether releases quarterly attestation report showing $118B reserves", date(2025, 2, 23), time(14, 0, 0), "neutral"),
        ("Why some analysts see bitcoin at $80K and others see $120K", date(2025, 2, 23), time(14, 30, 0), "neutral"),
        ("CoinDesk 20 Index Edges Up 0.2% in Quiet Holiday Trading", date(2025, 2, 23), time(15, 0, 0), "neutral"),
        ("Donald Trump's crypto policies: what's happened and what's next", date(2025, 2, 23), time(15, 30, 0), "neutral"),
        ("How stablecoins like USDC and USDT actually work", date(2025, 2, 23), time(16, 0, 0), "neutral")
    ]

    headlines = [item[0] for item in mock_data]
    dates     = [item[1] for item in mock_data]
    times     = [item[2] for item in mock_data]
    sentiments  = [item[3] for item in mock_data]

    return headlines, dates, times, sentiments 

mockHeadlines, mockDates, mockTimes, mockSentiments = getMockHeadlines()

testedHeadlines, testedSentiments, testedDates, testedTimes = sentiment([], True, [mockHeadlines, mockDates, mockTimes])



correctCount = 0 
totalCount = len(testedSentiments)
for i in range(totalCount):
    score = testedSentiments[i]
    if score > 0.15:
        score = "positive"
    elif score < -0.15:
        score = "negative"
    else:
        score = "neutral"
    if score == mockSentiments[i]:
        correctCount+= 1


accuracy = correctCount*100/totalCount
print(accuracy, "%")

