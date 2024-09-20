from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

chrome_driver_path = r"/Users/nyu/Documents/Ian's Folder/Misc/chromedriver-mac-arm64/chromedriver"

# Step 1: Set up the WebDriver (in this case for Chrome)
# You need to specify the path to your ChromeDriver

# Initialize the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Step 2: Open the website
url = 'https://www.ssense.com/en-us/men/bags?q=cdg'
driver.get(url)

# Optionally, wait for some seconds for the page to fully load
time.sleep(5)  # You can adjust this depending on your connection

# Step 3: Parse the page source using BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Step 4: Extract the product data (adjust based on SSENSE's HTML structure)
# Example of finding product descriptions
product_list = soup.find_all('div', class_='product-tile__description')

# Print out the products
for product in product_list:
    print(product.text)

# Step 5: Close the WebDriver after scraping
driver.quit()