import os, time, urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# importer les identifiants
from config import email, password, PROXY


# assurer que le press papier est vide
# userChamp.clear()
# passwordChamp.clear()


class Linkedin:
	def __init__(self, email, password, proxy):
		self.email = email
		self.password = password 
		self.proxy = proxy
		self.config()


	def config(self):
		options = Options()
		# AJOUT D'ADRESSES PROXY SI DEFINIT
		if self.proxy: 
			options.add_argument(f'--proxy-server={self.proxy}')
		self.chrome = webdriver.Chrome(os.path.abspath('driver\\chromedriver.exe'), options=options)


	def login(self):
		self.chrome.get('https://www.linkedin.com')

		# ciblage des champs necessaire
		userChamp = self.chrome.find_element_by_id('session_key')
		passwordChamp = self.chrome.find_element_by_id('session_password')
		loginBouton = self.chrome.find_element_by_class_name("sign-in-form__submit-button")

		userChamp.send_keys(email)
		passwordChamp.send_keys(password)

		loginBouton.click()


	def recherche(self, query, **filtre):
		# Pour encoder en url le mot cle 
		# en cas d'espace ou caractere speciaux 
		query = urllib.parse.quote(query)

		if filtre.get("personne"):
			type_ = "people"
		else:
			type_ = "all"
		
		url = f"https://www.linkedin.com/search/results/{type_}/?keywords={query}&origin=SWITCH_SEARCH_VERTICAL"
		self.chrome.get(url)

		elements = self.chrome.find_elements_by_class_name("search-result")

		return elements


	def close(self): self.chrome.close()



linkedin = Linkedin(email, password, PROXY)
linkedin.login()
res = linkedin.recherche("directeur technique", personne=True)