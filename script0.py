import os, re, time, datetime, urllib.parse, sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# importer les identifiants
from config import *



class Linkedin:
	def __init__(self, proxy=None):
		self.proxy = proxy
		self.config()
		self._initDb()
		self.logName = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
		# create file 
		with open("log/"+self.logName+".txt", "w"): pass  



	def config(self):
		# CREATION DOSSIER DE LOG
		if not os.path.isdir('log'):
			os.mkdir('log')
		if not os.path.isdir('log/images'):
			os.mkdir('log/images')

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
				message TEXT,
				nom TEXT
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
		
		reg = ""
		if filtre.get("ville"):
			if len(filtre.get("ville"))>0:
				# le variable est aleatoire entre ces deux
				# du coup je met les deux, il ne prendra pas encompte ce qu'il n'utilise pas
				reg = "geoUrn=" + urllib.parse.quote(filtre.get("ville")) + "&"
				reg += "facetGeoUrn=" + urllib.parse.quote(filtre.get("ville")) + "&"
		page = ""
		if filtre.get("page"):
			page = "&page=2"
		# generation du l'url de recherche
		url = f"https://www.linkedin.com/search/results/{type_}/?{reg}keywords={query}&origin=SWITCH_SEARCH_VERTICAL{page}"
		self.chrome.get(url)
		time.sleep(3)

		try:
		    element = WebDriverWait(self.chrome, 10).until(
		        EC.presence_of_element_located((By.TAG_NAME , "button"))
		    )
		finally:
		    self.ecrireLog("Aucun boutton trouvé")
		    self.captureEcran(suffix="_1")

		section = self.chrome.find_element_by_class_name("search-results-page")
		return section.find_elements_by_tag_name("li")
		


	def send_message_result(self, elements, message, temps):
		for block in elements:
			try:
				btn = block.find_element_by_tag_name('button')
				if btn.text.strip() in ("En attente", "Invitation envoyée"):
					continue
				link = block.find_element_by_tag_name('a')

				tmpuser = link.get_property('href').split('/')
				while tmpuser[-1].strip() == '':
					tmpuser = tmpuser[:-1]
				username = urllib.parse.unquote(tmpuser[-1])
				nom = link.text
				if self.verifName(username, message):
					# elem = self.chrome.switch_to.active_element
					btn.click()
					time.sleep(2)
					elem = self.chrome.switch_to.active_element
					for n in elem.find_elements_by_tag_name('button'):
						if n.text.strip() == "Ajouter une note":
							note = n 
						if n.text.strip() == "Envoyer":
							send = n
					note.click() 
					time.sleep(2)

					new_message = f"Bonjour {nom},\n" + message
					textarea = self.chrome.find_element_by_id('custom-message')
					textarea.clear() # On s'assure que c'est bien effacé
					textarea.send_keys(new_message)

					time.sleep(3)
					send.click()

					self.insertName(username, message, nom)
					self.ecrireLog(f"{username}: envoyé avec succès")
					time.sleep(temps)
				else:
					self.ecrireLog(f"{username}: deja envoyé")
			except Exception as err:
				self.ecrireLog(err)
			time.sleep(2)


	def insertName(self, username, message, nom):
		db = sqlite3.connect("__bot.db")
		cursor = db.cursor()

		cursor.execute("""
			INSERT INTO Cible (utilisateur, message, nom)
			VALUES (?, ?)
		""", (username, message, nom))
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


	def captureEcran(self, **args):
		try:
			hauteur = self.chrome.execute_script("""
				return document.body.parentNode.scrollHeight
			""")

			self.chrome.set_window_size(1920, hauteur)
		except: 
			pass
		finally:
			body = self.chrome.find_element_by_tag_name("body")
			body.screenshot("log/images/"+self.logName+f"{args.get('suffix')}.png")


	def ecrireLog(self, err):
		with open("log/"+self.logName+".txt", "a") as logFile:
			logFile.write(str(err) + "\n")



if __name__ == "__main__":
	# initialiser un bot linkedin
	linkedin = Linkedin(PROXY)

	try:
		# se connecter
		linkedin.login(email, password)
	except Exception as err:
		linkedin.ecrireLog(err)
		linkedin.captureEcran()
		linkedin.chrome.close()
		exit()

	for page in range(pages):
		page += 1
		print(f"Entrant dans la {page} page")
		try:
			# rechercher
			res = linkedin.recherche(mot_cle, personne=True, ville=ville, page=page)
		except Exception as err:
			linkedin.ecrireLog(err)
			linkedin.captureEcran()
			linkedin.chrome.close()
			exit()

		# envoyer message aux resultat
		try:
			linkedin.send_message_result(res, message, interval_temps)
		except Exception as err:
			linkedin.ecrireLog(err)
			linkedin.captureEcran()
			linkedin.chrome.close()
			exit()
	time.sleep(5)

	linkedin.chrome.execute_script("""
		alert('Tâche terminé')
	""")