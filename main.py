import selenium 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
import json
from time import sleep
from urllib.parse import urlparse

def clean(string) -> float:
    string = string.replace("₹", "")
    string = string.replace(",", "")
    return float(string)

def send_to_telegram(message):
    if not TOKEN:
        return
    for chat_id in CHAT_IDS:
        if not chat_id:
            continue
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url)

sleep_frequency = 5 # in minutes wait after every 1 cycle
driver = webdriver.Chrome()
with open("data.json", "r") as f:
    data = json.load(f)

TOKEN = data["telegram"]["token"]
CHAT_IDS = data["telegram"]["chat_id"]

# create history.txt file if not exists
try:
    open("history.txt", "x", encoding="utf-8")
except FileExistsError:
    pass
else:
    with open("history.txt", "w", encoding="utf-8") as f:
        f.write("")

for page_count in range(1, 11):
    url = data["top_deals_url"]
    if page_count > 1:
        url += f"&page={page_count}"
    driver.get(url)
    sleep(5)
    page_count += 1
    with open("history.txt", "r", encoding="utf-8") as f:
        history = f.read().split("\n")
    names = []

    for product in driver.find_elements(By.XPATH, "//div[@data-uuid and @data-index]"):
        try:
            offered_price = product.find_element(By.CLASS_NAME, "a-price-whole").text
        except selenium.common.exceptions.NoSuchElementException:
            continue
        offered_price = clean(offered_price)
        try:
            original_price = product.find_element(By.CLASS_NAME, "a-text-price").text
            original_price = clean(original_price)
        except selenium.common.exceptions.NoSuchElementException:
            original_price = offered_price
        name = str(product.find_element(By.CLASS_NAME, "a-size-base-plus").text)
        image = str(product.find_element(By.CLASS_NAME, "s-image").get_attribute("src"))
        link = str(product.find_element(By.CLASS_NAME, "a-link-normal").get_attribute("href"))
        link = urlparse(link)
        link = link._replace(query="").geturl() # remove the query string from the url
        if "/dp/" not in link:
            continue
        if name in history:
            continue
        discount = int(round((1 - (offered_price / original_price)) * 100, 2))
        if discount >= data["discount_threshold"]:
            message = f"{discount}% off\n ₹{int(offered_price)}\n{link}"
            send_to_telegram(message)
            print("Message sent to telegram")
        names.append(name)
    # write all the links to history.txt file
    with open("history.txt", "a+", encoding="utf-8") as f:
        f.write("\n".join([name.replace("\n", " ") for name in names]))
    sleep(sleep_frequency)

driver.close()

    

    
