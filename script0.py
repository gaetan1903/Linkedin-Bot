import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# importer les identifiants
from config import email, password

chrome = webdriver.Chrome(os.path.abspath('driver\\chromedriver.exe'))

chrome.get('https://www.linkedin.com')

# ciblage des champs necessaire
userChamp = chrome.find_element_by_id('session_key')
passwordChamp = chrome.find_element_by_id('session_password')
loginBouton = chrome.find_element_by_class_name("sign-in-form__submit-button")

# assurer que le press papier est vide
userChamp.clear()
passwordChamp.clear()

userChamp.send_keys(email)
passwordChamp.send_keys(password)
loginBouton.click()

#chrome.close()