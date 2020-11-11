import os, time, urllib.parse, sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# importer les identifiants
from config import *


# assurer que le press papier est vide
# userChamp.clear()
# passwordChamp.clear()




class Linkedin:
	def __init__(self, proxy):
		self.proxy = proxy
		self.config()
		self._initDb()


	def config(self):
		options = Options()
		# AJOUT D'ADRESSES PROXY SI DEFINIT
		if self.proxy: 
			options.add_argument(f'--proxy-server={self.proxy}')
		self.chrome = webdriver.Chrome(os.path.abspath('driver\\chromedriver.exe'), options=options)
		self.chrome.maximize_window()


	def _initDb(self):
		db = sqlite3.connect("__bot.db")
		cursor = db.cursor()

		cursor.execute("""
			CREATE TABLE IF NOT EXISTS Cible 
			(
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				utilisateur TEXT,
				message TEXT 
			)
		""")

		db.commit()
		db.close()


	def login(self, email, password):
		self.chrome.get('https://www.linkedin.com')

		# ciblage des champs necessaire
		userChamp = self.chrome.find_element_by_id('session_key')
		passwordChamp = self.chrome.find_element_by_id('session_password')
		loginBouton = self.chrome.find_element_by_class_name("sign-in-form__submit-button")
		time.sleep(1)
		userChamp.send_keys(email)
		time.sleep(1)
		passwordChamp.send_keys(password)
		time.sleep(1)
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
		time.sleep(3)

		section = self.chrome.find_element_by_class_name("search-results-page")
		return section.find_elements_by_tag_name("li")
		


	def send_message_result(self, elements, message, temps):
		for block in elements:
			btn = block.find_element_by_tag_name('button')
			if btn.text.strip() == "En attente": continue
			link = block.find_element_by_tag_name('a')
			username = link.get_property('href').split('/')[-1] 
			
			if self.verifName(username, message):
				elem = self.chrome.switch_to.active_element
				btn.click()
				time.sleep(2)
				for n in elem.find_elements_by_tag_name('button'):
					if n.text.strip() == "Ajouter une note":
						note = n 
					if n.text.strip() == "Envoyer":
						send = n
				note.click() 
				time.sleep(2)
				new_message = "Bonjour ,\n" + message
				textarea = self.chrome.find_element_by_id('custom-message')
				textarea.send_keys(new_message)

				time.sleep(3)
				send.click()

				self.insertName(username, message)
				time.sleep(temps)

		print("tapitra ve? " + str(len(elements)))


	def insertName(self, username, message):
		db = sqlite3.connect("__bot.db")
		cursor = db.cursor()

		cursor.execute("""
			INSERT INTO Cible (utilisateur, message)
			VALUES (?, ?)
		""", (username, message))
		db.commit()
		db.close()


	def verifName(self, username, message):
		db = sqlite3.connect("__bot.db")
		cursor = db.cursor()
		cursor.execute("""
			SELECT 1
			FROM Cible 
			WHERE utilisateur = ?
			AND message = ?
		""", (username, message))

		res = cursor.fetchall()
		db.close()

		return True if len(res) == 0 else False 


if __name__ == "__main__":

	# initialiser un bot linkedin
	linkedin = Linkedin(PROXY)

	# se connecter
	linkedin.login(email, password)

	# rechercher
	res = linkedin.recherche(mot_cle, personne=True)

	# envoyer message aux resultat
	linkedin.send_message_result(res, message, interval_temps)