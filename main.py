import pandas as pd
import sqlite4
import datetime as datetime
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Access the API key
forex_api_key = os.getenv("FOREX_API_KEY")
