from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Set up options to use a custom User-Agent
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Set up the WebDriver (in this case for Chrome)
# You need to specify the path to your ChromeDriver
chrome_driver_path = r"/Users/ianchang/Library/Mobile Documents/com~apple~CloudDocs/1. Project/chromedriver-mac-x64/chromedriver"

# Initialize the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Open the website
url = 'https://www.artnet.com/auctions/all-artworks/'
driver.get(url)

time.sleep(5)

# Parse the page source using BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Extract the product data (adjust based on SSENSE's HTML structure)
# Example of finding product descriptions
product_list = soup.find_all('div', class_='details')

# Print out the products
for product in product_list:
    print(product.text)

# Close the WebDriver after scraping
driver.quit()

print(product_list)