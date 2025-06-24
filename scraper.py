from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.Chrome()

options.get("https://www.tradeindia.com/tradeshows/apparel-fashion/")
element = options.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div/div[3]/div[1]/div[2]/div[1]/div")

print(element.text)