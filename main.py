import os
import time
import random
from dotenv import load_dotenv

import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup

import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

art_list = []

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
]

for n in range(1,5):
    # Rotate user-agent
    user_agent = random.choice(user_agents)
    # Set up options to use a custom User-Agent
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={user_agent}")

    # Set up the WebDriver (in this case for Chrome)
    # You need to specify the path to your ChromeDriver
    chrome_driver_path = r"/Users/ianchang/Library/Mobile Documents/com~apple~CloudDocs/1. Project/chromedriver-mac-x64/chromedriver"

    # Initialize the WebDriver
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the website
    url = f'https://www.artnet.com/auctions/all-artworks/{n}'
    driver.get(url)

    # Parse the page source using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract the artwork data 
    artworks = soup.find_all('div', class_='details')
    art_list += artworks 

    # Close the WebDriver after scraping
    driver.quit()
    
    # Introduce a random delay to avoid bot detection (2-6 seconds)
    time.sleep(random.uniform(2, 6))

artNetDict = {}

for index, art in enumerate(art_list, 1):
    artist_element = art.find("li", class_ = "ng-binding")
    if artist_element:
        artist_name = artist_element.text.strip()
    else:
        print(f"Missing artist name")
        continue

    piece_element = art.find("em", class_ = "ng-binding")
    if piece_element:
        piece_name = piece_element.text.strip()
    else:
        print(f"Missing piece name")
        continue

    price_element = art.find('li', class_="ng-binding ng-scope").text.strip()
    if "Bids" in price_element:
        price_text, bid_text = price_element.split(" (")
        price, currency = price_text.split(" ")
        price = float(price.replace(",", ""))
        bids = int(bid_text.replace("Bids)",""))
    elif "Bid" in price_element:
        price_text, bid_text = price_element.split(" (")
        price, currency = price_text.split(" ")
        price = float(price.replace(",", ""))
        bids = 1
    else:
        price_range, currency = price_element.split(" ")
        lower_bound, upper_bound = price_range.split("—")
        lower_bound = float(lower_bound.replace(",",""))
        upper_bound = float(upper_bound.replace(",",""))
        price = float(np.mean([lower_bound, upper_bound]))
        bids = 0

    expiration_element = art.find('li', {"ng-class": "{'red' : brick.Remaining.Days <= 0}"}).text.strip()
    if expiration_element:
        expiration, daysText, remainingText = expiration_element.split(" ")
        expiration = int(expiration)
    
    # print(artist_name, piece_name, price, currency, bids) -> to see if it all turned out okay
    
    artNetDict[index] = {}
    artNetDict[index]["Name"] = artist_name
    artNetDict[index]["Piece"] = piece_name
    artNetDict[index]["CurrentPrice"] = price
    artNetDict[index]["Currency"] = currency
    artNetDict[index]["NumBids"] = bids
    artNetDict[index]["DaysLeft"] = expiration

col_names = ["Artist", "Name of Piece", "Current Price", "Currency", "Num of Bids", "Days Left"]
art_df = pd.DataFrame(columns=col_names)

for key, value in artNetDict.items():
    row = pd.DataFrame({"Artist": [value["Name"]], "Name of Piece": [value["Piece"]], "Current Price": [value["CurrentPrice"]], "Currency": [value["Currency"]], "Num of Bids": [value["NumBids"]], "Days Left": [value["DaysLeft"]]})
    art_df = pd.concat([art_df, row], ignore_index= True)

art_df = art_df.sort_values(by=["Days Left"], ascending= True).reset_index().drop(columns=["index"])

unique_artists = []

for n in range(0,len(art_df.Artist.unique())):
    name = art_df.Artist.unique()[n]
    print(name)
    unique_artists.append(name)
