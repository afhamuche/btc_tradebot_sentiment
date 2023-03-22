#!/usr/bin/env python3

import requests
import json
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import csv
import requests
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time

def get_ticker_price():
    price = requests.get('https://www.mercadobitcoin.net/api/BTC/ticker/')
    price = json.loads(price.text)
    return float(price['ticker']['last'])

def extract(trades, a_key):
    extract = []
    for trade in trades:
        extract.append(trade[a_key])
    return extract

def get_trades(seconds):
    time_now = int(time.time())
    time_then = time_now - seconds
    trades = requests.get('https://www.mercadobitcoin.net/api/BTC/trades/{0}/{1}'.format(time_then, time_now))
    return trades.json()

# Set up the News API client
newsapi = NewsApiClient(api_key='newsapikey')

# Define the search term and the number of articles to retrieve
search_term = 'bitcoin'
num_articles = 25



while True:

    # Retrieve the news articles from the News API
    articles = newsapi.get_everything(q=search_term, language='en', sort_by='relevancy', page_size=num_articles)

    # Initialize the sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Set sum of sentiments
    sentiment_sum = 0

    # Loop through each article and analyze its sentiment
    for article in articles['articles']:
        title = article['title']
        description = article['description']
        content = article['content']

        # Combine the article text
        article_text = title + ' ' + description + ' ' + content if content else title + ' ' + description

        # Analyze the sentiment of the article
        sentiment = "%.2f" % analyzer.polarity_scores(article_text)['compound']

        # Sum all sentiment
        sentiment_sum += float(sentiment)

        # Get sentiment average
        sentiment_avg = float("%.2f" % (sentiment_sum/num_articles))

    # Get the historical data
    trades = get_trades(600)
    timestamps = extract(trades, 'date')
    prices = extract(trades, 'price')

    # Perform linear regression on the prices
    x = np.array(timestamps).reshape(-1, 1)
    y = np.array(prices).reshape(-1, 1)
    reg = LinearRegression().fit(x, y)
    reg_value = "%.6f" % float(reg.predict(np.array([[timestamps[-1]]]))[0][0])

    # Get the current price
    current_price = "%.6f" % get_ticker_price()

    # Determine whether to buy or sell
    if current_price > reg_value and sentiment_avg >= -0.05:
        trade_type = 'buy'
    else:
        trade_type = 'sell'

    # Write output to a csv file
    with open('output.csv', 'a', newline='') as cfile:
        writer = csv.writer(cfile)

        # Collect the data and append to csv
        data = [int(time.time()), trade_type, current_price, reg_value, sentiment_avg]
        writer.writerow(data)

    print(data)
    time.sleep(20)
