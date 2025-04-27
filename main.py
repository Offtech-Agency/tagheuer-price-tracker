import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
import os

PRODUCT_URL = 'https://www.tagheuer.com/ca/en/timepieces/'

DATA_FILE = 'prices.json'
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        old_prices = json.load(f)
else:
    old_prices = {}

def scrape_prices():
    page = requests.get(PRODUCT_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(page.content, 'html.parser')

    products = soup.select('div.product-tile')
    prices = {}

    for product in products:
        title_elem = product.select_one('a.product-name-link')
        price_elem = product.select_one('div.product-sales-price')

        if title_elem and price_elem:
            title = title_elem.text.strip()
            price = price_elem.text.strip()
            prices[title] = price

    return prices

def check_price_changes(old, new):
    changes = []
    for title, price in new.items():
        if title not in old or old[title] != price:
            changes.append(f"{title}: {old.get(title, 'N/A')} -> {price}")
    return changes

def send_email(body):
    msg = MIMEText(body)
    msg['Subject'] = 'TAG Heuer Price Changes Detected'
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_TO')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
    server.send_message(msg)
    server.quit()

new_prices = scrape_prices()
changes = check_price_changes(old_prices, new_prices)

if changes:
    print('Price changes detected!')
    send_email('\n'.join(changes))

with open(DATA_FILE, 'w') as f:
    json.dump(new_prices, f, indent=4)
