import os
from datetime import date
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

def get_listing(page_depth):
    '''
    Scrapes artwork listings from ArtNet up to the given page depth.
    page_depth must be an integer value indicating the number of pages to scrape.
    For this prototype version, we recommend that you scroll down all the way through the bottom of ArtNet's listings to see how many pages there are when you run this code.
    '''
    # Initialize an empty list to store artwork information
    art_list = []

    # List of user-agents to rotate to mimic human browsing and avoid bot detection
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    ]

    for n in range(1,page_depth+1):
        # Rotate user-agent randomly
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

        # Find all div elements with class 'details' that contain artwork information
        artworks = soup.find_all('div', class_='details')
        art_list += artworks # Add the scraped artworks to the art_list

        # Close the WebDriver after scraping
        driver.quit()
        
        # Introduce a random delay to avoid bot detection (2-6 seconds)
        time.sleep(random.uniform(2, 6))

    return art_list # Return the list of artworks from all pages

def get_df_of_listings(page_depth):
    '''
    Extracts relevant information from the listing pages and returns a DataFrame containing the artist name, piece name, current price, currency, number of bids, and days left.
    '''
    # Scrape the listing pages
    art_list = get_listing(page_depth)
    # Initialize list for artwork data
    art_data = []
    
    for index, art in enumerate(art_list, 1):
        # Extract the artist name
        artist_element = art.find("li", class_ = "ng-binding")
        if artist_element:
            # Clean and store the artist's name
            artist_name = artist_element.text.strip()
        else:
            # skip if the name's missing
            print(f"Missing artist name")
            continue

        # Extract the name of the artwork
        piece_element = art.find("em", class_ = "ng-binding")
        if piece_element:
            # Clean and store the piece's title
            piece_name = piece_element.text.strip()
        else:
            # and skip if not found
            print(f"Missing piece name")
            continue

        # Extract the current price and number of bids
        price_element = art.find('li', class_="ng-binding ng-scope").text.strip()
        if "Bids" in price_element:
            # Split price and bid 
            price_text, bid_text = price_element.split(" (")
            # Split price and currency notation
            price, currency = price_text.split(" ")
            # Convert the price into a float variable
            price = float(price.replace(",", ""))
            # Extract the number of bids
            bids = int(bid_text.replace("Bids)",""))
        elif "Bid" in price_element:
            # This means there's only one bid at the moment
            price_text, bid_text = price_element.split(" (")
            price, currency = price_text.split(" ")
            price = float(price.replace(",", ""))
            # default to 1 bid
            bids = 1
        else:
            # If there isn't a single bid at the moment, we calculate the average price based on the range provided and store it as the price value
            price_range, currency = price_element.split(" ")
            lower_bound, upper_bound = price_range.split("—")
            lower_bound = float(lower_bound.replace(",",""))
            upper_bound = float(upper_bound.replace(",",""))
            price = float(np.mean([lower_bound, upper_bound]))
            # default to 0 bids
            bids = 0

        # Extract the number of days left until the auction ends for that particular piece
        # 9-23-24 Update: Only now realizing that the notation changes to  XX hours remaining once expiration date gets within a day
        # Thankfully, the class notation remains the same
        expiration_element = art.find('li', {"ng-class": "{'red' : brick.Remaining.Days <= 0}"}).text.strip()
        if expiration_element:
            # extract the expiration value and turn it into an integer
            expiration, days_or_hours, remainingText = expiration_element.split(" ")
            if days_or_hours == "days":
                daysleft = int(expiration)
                # Store the artwork information in a dictionary and append to the list
                art_data.append({
                    "Artist": artist_name,
                    "Name of Piece": piece_name,
                    "Current Price": price,
                    "Currency": currency,
                    "Num of Bids": bids,
                    "Time Left": daysleft,
                    "Days/Hours": "Days"
                    })
            elif days_or_hours == "hours":
                hoursleft = int(expiration)
                art_data.append({
                    "Artist": artist_name,
                    "Name of Piece": piece_name,
                    "Current Price": price,
                    "Currency": currency,
                    "Num of Bids": bids,
                    "Time Left": hoursleft,
                    "Days/Hours": "Hours"
                    })
    
    # Turn the list of dictionaries into a pandas dataframe
    art_df = pd.DataFrame(art_data)

    # Sor the dataframe by remaining time
    art_df = art_df.sort_values(by=["Days/Hours","Time Left"], ascending= [False, True]).reset_index(drop=True)

    # Return the dataframe containing the current listings
    return art_df


def get_unique_artists(artwork_dataframe):
    '''
    Extracts and returns a list of unique artist names from the DataFrame.
    '''
    # Initialize an empty list to store unique artist names
    unique_artists = []

    # Extract unique artist names and append them to the list
    for n in range(0,len(artwork_dataframe.Artist.unique())):
        name = artwork_dataframe.Artist.unique()[n]
        unique_artists.append(name)
    # Return the list of unique artist names present in the dataframe
    return unique_artists

# Reddit r/Art portion:

# Load environment variables
load_dotenv()

# Initialize Reddit API with relevant credentials stored in .env file
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    username=os.getenv('REDDIT_USERNAME'),
    password=os.getenv('REDDIT_PASSWORD')
)

def get_sentiment_score(artist_name):
    '''
    Searches for discussions about the artist on Reddit (r/Art) and computes the average sentiment score.
    '''
    # Initialize a list to store comments
    commentList = []

    # Search Reddit for artist
    submissions = reddit.subreddit("Art").search(f"{artist_name.lower()}", sort = "relevance")
    
    for submission in submissions:
        # Expand hidden comments
        submission.comments.replace_more(limit=0)  # Expand the "load more" comments
        for top_level_comment in submission.comments:
            # Check if comment has a body (not deleted or removed)
            if top_level_comment.body:
                # Append it to the comments list 
                commentList.append(top_level_comment.body.lower())

    # Initialize VADER sentiment analysis tool
    sentiment_analyzer = SentimentIntensityAnalyzer()

    # Initialize a list to store the compound scores
    compound_scores = []
    
    # Analyze sentiment of each comment
    for comment in commentList:
        vs = sentiment_analyzer.polarity_scores(comment)
        # Append the compound score to the list above
        compound_scores.append(vs["compound"])
    
    # Calculate the mean sentiment score; default to 0 if no score was calculated
    if len(compound_scores) > 0:
        mean_score = float(np.mean(compound_scores))
    elif len(compound_scores) == 0:
        mean_score = 0.0
    
    # Return the average sentiment score
    return mean_score

def get_artist_score_df(artist_names_list):
    '''
    Generates a DataFrame containing the sentiment scores for a list of artists.
    '''
    # Initialize a list to store the compound scores for each of the artists found in the listing
    scores_list = []

    for name in artist_names_list:
        # Get sentiment score for each artist
        score = get_sentiment_score(name)
        # Append the result as a dictionary
        scores_list.append({"Artist": name, "Sentiment Score": score})
    # Convert the list to pandas dataframe
    scores_df = pd.DataFrame(scores_list)
    
    # Return the dataframe of sentiment scores
    return scores_df

# Get artwork listings and unique artists
current_listings_df = get_df_of_listings(4)
current_artists_list = get_unique_artists(current_listings_df)
current_scores_df = get_artist_score_df(current_artists_list)

def get_final_df(df_of_listings, df_of_scores, disposable_income):
    '''
    Merges artwork listings with sentiment scores and provides bid recommendations based on sentiment and budget.
    '''

    print(f"Based on your budget of {disposable_income}, here are our recommendations in a dataframe form...")
    
    # Merge listings and sentiment scores DataFrames on the Artist column
    merged_df = pd.merge(df_of_listings, df_of_scores, how="left", left_on="Artist", right_on="Artist")
    
    # Iterate over each row and decide whether to recommend bidding or not based on the sentiment score and current price vs. budget/limit price
    for index, row in merged_df.iterrows():
        if row["Sentiment Score"] >= 0.1 and row["Current Price"] < disposable_income:
            merged_df.loc[index, "Bid Action"] = "Bid Higher"
        else:
            merged_df.loc[index, "Bid Action"] = "Do Not Bid"
    
    # Return the DataFrame with bid recommendations
    return merged_df

# Get user's budget
limit_price = float(input("How much are you willing to spend on a piece of artwork? "))

# Generate recommendations based on sentiment scores and budget
recs_df = get_final_df(current_listings_df, current_scores_df, limit_price).sort_values(by=["Sentiment Score","Days/Hours","Time Left"], ascending= [False, False, True])

# Export the recommendations to a CSV file
today_date = date.today()
recs_df.to_csv(f"bid_recs_{today_date}.csv", index=False)

# print the recommended bids (Post-deadline add-on created on 9-23-24)
print(f"These are our recommended bids:\n")
for index, row in recs_df.iterrows():
    artistname = row.Artist
    piecename = row["Name of Piece"]
    price = row["Current Price"]
    numbids = row["Num of Bids"]
    timeleft = row["Time Left"]
    daysorhours = row["Days/Hours"]
    if row["Bid Action"] == "Bid Higher":
        print(f"{piecename} by {artistname} is going for $ {price:,.2f} and has {numbids} bid(s) with {timeleft} {daysorhours.lower()} left\n")