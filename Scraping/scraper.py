from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import pandas as pd

import requests
import os
import re
import time
import random

import warnings
warnings.filterwarnings('ignore')

# Config------------------------------

# OS Config
DATA_FOLDER_PATH = os.getcwd() + '\\..\\data'
PROVINCE_NAME = 'Cavite'

# Soup Config
URL = 'https://danielsecotravels.com/cavite-tourist-spot/'
TAG = 'h4'
ID = None
CLASS_ = None

# Selenium Config
WEBDRIVER_PATH = os.getcwd() + '\\chromedriver\\chromedriver.exe'

# Filter Words config:
FILTER_WORDS = [
    'type',
    'location',
    'description'
]


# Code------------------------------------

RANK_PATTERN = '\d+\.'

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}

def get_html(path):
    r = requests.get(path)
    return r.text

def find_destinations(soup):
    if ID:
        val = soup.find_all(id=ID)
    elif CLASS_:
        val = soup.find_all(class_=CLASS_)
    elif TAG:
        val = soup.find_all(TAG)
    else:
        raise Exception("ID, CLASS_, and TAG is null. One must be filled in!")

    destinations = []
    for v in val:
        txt = v.get_text()
        if re.match(RANK_PATTERN, txt):
            destinations.append(re.sub(RANK_PATTERN, '', txt).strip())
        else:
            destinations.append(txt.strip())

    return destinations

def find_kinds(destinations):
    # Initialize Driver
    driver = webdriver.Chrome(WEBDRIVER_PATH)

    # Visit google.com
    driver.get('https://www.google.com')

    # Initialize container for kinds
    kinds = []

    for destination in destinations:
        # Get the Searchbox object
        searchbox = driver.find_element_by_name('q')

        # Clear if it is not cleared
        searchbox.clear()

        # Buffer
        time.sleep(random.randint(1, 2))

        # Enter the query
        searchbox.send_keys(f"{destination} description")
        searchbox.send_keys(Keys.RETURN)

        # Add Buffer
        time.sleep(random.randint(1, 2))

        # Get the kind
        soup = BeautifulSoup(driver.page_source)
        kind = soup.find_all('b')

        if kind:
            filtered = []

            for k in kind:
                to_add = False
                text = k.get_text()
                for filter in FILTER_WORDS:
                    if not re.match(filter, text.lower()):
                        to_add = True
                if to_add:
                    filtered.append(text)

            kinds.append(filtered[0])
        else:
            kind = soup.find_all('em')
            if kind:
                filtered = []

                for k in kind:
                    to_add = False
                    text = k.get_text()
                    for filter in FILTER_WORDS:
                        if not re.match(filter, text.lower()):
                            to_add = True
                    if to_add:
                        filtered.append(text)

                kinds.append(filtered[0])
            else:
                kind = soup.find_all('strong')
                if kind:
                    filtered = []

                    for k in kind:
                        to_add = False
                        text = k.get_text()
                        for filter in FILTER_WORDS:
                            if not re.match(filter, text.lower()):
                                to_add = True
                        if to_add:
                            filtered.append(text)

                    kinds.append(filtered[0])
                else:
                    raise Exception('Cannot find important description!')


        print('-'*20)
        print(destination,': ', kind[0])
        print('-'*20)

        # Add Buffer
        time.sleep(random.randint(1, 2))

    driver.quit()

    return kinds
  
def main():
    html = get_html(URL)
    soup = BeautifulSoup(html, 'html.parser')

    # Get the Destination List
    destinations = find_destinations(soup)

    # Get the kind List
    kinds = find_kinds(destinations)

    # Create a DataFrame
    df = pd.DataFrame({'Location Name': destinations, 'Location Kind': kinds})
    
    df.to_csv(DATA_FOLDER_PATH + f'\\{PROVINCE_NAME}.csv', index=False)

if __name__ == '__main__':
    main()