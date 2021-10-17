import numpy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import time
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import bs4 as bs
from bs4 import BeautifulSoup
import requests
import newspaper
import urllib3.request, sys, time

feed = "https://www.globaltimes.cn"

response = requests.get(feed)

webpage = response.content

soup = BeautifulSoup(webpage, features='xml')

items = soup.find_all('item')

articles = []
for item in items:
    link = item.find('link').text
    articles.append(link)

authorname = []
title = []
thearticle = []
date = []

for link in items:
    # store the text for each article
    paragraphtext = []
    # get url
    url = link
    # get page text
    page = requests.get(url)
    # parse with BFS
    soup = BeautifulSoup(page.text, 'html.parser')
    # get author name, if there's a named author
    try:
        abody = soup.find(class_='byline').find('a')
        aname = abody.get_text()
    except:
        aname = 'Anonymous'

    # get article title
    atitle = soup.find(class_="article_title")
    thetitle = atitle.get_text()
    # get article date
    adate = soup.find(class_="pub_time")
    datetime = adate.get_text()
    # get main article page
    articlebody = soup.find(class_='article_page')
    # get text
    articletext = soup.find_all('p')[8:]
    # print text
    for paragraph in articletext[:-1]:
        # get the text only
        text = paragraph.get_text()
        paragraphtext.append(text)
    # combine all paragraphs into an article
    thearticle.append(paragraphtext)
    authorname.append(aname)
    title.append(thetitle)

# join paragraphs to re-create the article
myarticle = [' '.join(article) for article in thearticle]

# save article data to file
data = {'Title': title,
        'Author': authorname,
        'PageLink': items,
        'Article': myarticle,
        'Date': datetime}

oldnews = pd.read_excel('GTnews.xlsx')
news = pd.DataFrame(data=data)
cols = ['Title', 'Author', 'PageLink', 'Article', 'Date']
news = news[cols]

afronews = oldnews.append(news)
afronews.drop_duplicates(subset='Title', keep='last', inplace=True)
afronews.reset_index(inplace=True)
afronews.drop(labels='index', axis=1, inplace=True)

filename = 'GTnews.xlsx'
wks_name = 'Data'

writer = pd.ExcelWriter(filename)
afronews.to_excel(writer, wks_name, index=False)

writer.save()
