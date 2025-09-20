import requests
from bs4 import BeautifulSoup


days = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12","13", "14", "15", "16", "17", "18", "19", "20", "21" ]
#days = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11"]
#months =["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
months =["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
#years = ["2020", "2021"]
years = ["2024"]
pages = [1, 2, 3]
all_news = []
for year in range(len(years)):
    for month in range(len(months)):
        for  day in range(len(days)):
            for page in range(len(pages)):
                url = f"https://www.wsj.com/news/archive/{years[year]}/{months[month]}/{days[day]}?page={pages[page]}"


                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content,'html.parser')
                text = soup.findAll('span', class_='WSJTheme--headlineText--He1ANr9C')

                for i in range(len(text)):
                    startIndex = str(text[i]).find(">") + 1
                    endIndex = str(text[i]).rfind("<")
                    text[i] = str(text[i])[startIndex:endIndex]
                    all_news.append(f"{days[day]}/{months[month]}/{years[year]} {text[i]}")
                

for headline in all_news:
    if "Bitcoin" in headline or "bitcoin" in headline:
        print(headline)

