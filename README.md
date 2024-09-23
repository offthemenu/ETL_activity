# To Bid or Not To Bid

This Python project scrapes artwork listings from ArtNet Auctions and combines sentiment analysis from Reddit discussions to provide recommendations on whether to bid on an artwork based on both price and sentiment. It helps art enthusiasts make informed decisions by analyzing public opinion and auction data.

## Features

### Web Scraping of Art Listings: 
Collects information about artworks (**artist, title, current bid, price range, expiration time)** from *ArtNet Auctions*.  
### Reddit Sentiment Analysis: 
Leverages Reddit's r/Art subreddit to gauge public sentiment on artists by analyzing comments and determining overall positivity.   
### Bid Recommendations: 
Merges the auction data with sentiment analysis to generate recommendations based on a user's budget and the public's perception of the artist.
### Data Export: 
Generates a CSV file of the recommended actions for bidding, making it easy to view and act on the suggestions.

## Usage

### Scraping Art Listings

The script scrapes art auction listings from ArtNet based on the specified page depth.  

For this prototype version, we recommend that you scroll down all the way through the bottom of ArtNet's listings to see how many pages there are when you run this code.

```py
current_listings_df = get_df_of_listings(page_depth=4)
```

You can adjust page_depth to control how many pages of listings are scraped.

### Retrieving Artist Sentiment

The script performs sentiment analysis on artists by searching Reddit’s r/Art subreddit for discussions about each artist:

```py
current_artists_list = get_unique_artists(current_listings_df)
current_scores_df = get_artist_score_df(current_artists_list)
```

### Generating Bid Recommendations

Input your disposable income, and the script will generate recommendations based on the current sentiment scores and the auction listings:

```python
limit_price = float(input("How much are you willing to spend on a piece of artwork? "))
recs_df = get_final_df(current_listings_df, current_scores_df, limit_price)
```

This outputs a CSV file (e.g., bid_recs_2024-09-21.csv) with the following columns:

Artist | Name of Piece | Current Price | Currency | Num of Bids | Days Left | Sentiment Score | Bid Action

## How It Works
### Web Scraping: 
Using Selenium and BeautifulSoup, the script scrapes the listing information from ArtNet auctions.

### Reddit Sentiment Analysis: 
The praw library is used to query Reddit's r/Art subreddit for discussions on each artist. The comments are analyzed using VADER Sentiment Analysis to generate a compound sentiment score for each artist.
### Bid Recommendation: 
By merging the auction data with sentiment analysis and considering your disposable income, the script suggests which pieces are worth bidding on based on public interest and affordability.
## Dependencies
**Selenium** – for web scraping ArtNet auctions.  
**BeautifulSoup4** – for HTML parsing.  
**praw** – for interacting with the Reddit API.  
**vaderSentiment** – for sentiment analysis.  
**pandas** – for data manipulation.  
**numpy** – for numerical operations.  
## Future Improvements  
Add support for more auction platforms.  

Expand sentiment analysis to other social media platforms.  
