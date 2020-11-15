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
				nom_complet TEXT
			)
		""")

		db.commit()
		db.close()



	def login(self, email, password):
		self.chrome.get('https://www.linkedin.com/login/fr?fromSignIn=true')
		time.sleep(ATTENTE_PAGE)
		# ciblage des champs necessaire
		userChamp = self.chrome.find_element_by_id('username')
		passwordChamp = self.chrome.find_element_by_id('password')
		loginBouton = self.chrome.find_element_by_xpath("//button[@type='submit']")
	
		userChamp.send_keys(email)
		time.sleep(INPUT_ATTENTE)

		passwordChamp.send_keys(password)
		time.sleep(INPUT_ATTENTE)

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
			page = f"&page={filtre.get('page')}"

		# generation du l'url de recherche
		url = f"https://www.linkedin.com/search/results/{type_}/"
		# les parametres pour l'url
		url += f"?{reg}keywords={query}&origin=SWITCH_SEARCH_VERTICAL{page}"
		self.chrome.get(url)
		time.sleep(ATTENTE_PAGE)

		section = self.chrome.find_element_by_xpath("//ul[contains(@class, 'search-result')]")
		return section.find_elements_by_tag_name("li")
		


	def send_message_result(self, elements, message):
		for block in elements:
			try:
				link = block.find_element_by_tag_name('a')
			except: 
				self.ecrireLog(f"la balise a n'est pas trouvé dans:\n------- DEBUT HTML -------- {block.get_attribute('outerHTML')}\n ------- FIN HTML --------\n\n\n")
				continue

			# extraction du nom d'utilisateur du lien 
			tmpuser = link.get_property('href').split('/')
			while tmpuser[-1].strip() == '':
				tmpuser = tmpuser[:-1]
			username = urllib.parse.unquote(tmpuser[-1])

			# prendre le nom complet de la personne
			nomComplet = link.text
			if nomComplet.strip() == '':
				# on essaie de le prendre par l'username
				nomComplet = self.getName(username)

			print(f"Tour de {nomComplet} as {username}")
			try:
				btn = WebDriverWait(block, 3).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Se connecter']")))
			except Exception as err:
				self.ecrireLog(f"{nomComplet}: Ne peut pas etre envoyée de message\n------- DEBUT HTML -------- {block.get_attribute('outerHTML')}\n ------- FIN HTML --------\n\n\n")
				block.screenshot(f"log/images/{self.logName}_{nomComplet}.png")
				continue  

			if self.verifName(username, message):
				btn.click()
				time.sleep(ATTENTE_BOUTON)

				elem = self.chrome.switch_to.active_element

				try:
					note = elem.find_element_by_xpath("//button//span[text()='Ajouter une note']")
				except: 
					self.ecrireLog(f"{nomComplet}: //button//span[text()='Ajouter une note'] pas trouvé in \n------- DEBUT HTML -------- {elem.get_attribute('outerHTML')}\n ------- FIN HTML --------\n\n\n")
					continue
					
				try:
					send = elem.find_element_by_xpath("//button//span[text()='Envoyer']")
				except: 
					self.ecrireLog(f"{nomComplet}: //button//span[text()='Envoyer'] pas trouvé in \n------- DEBUT HTML -------- {elem.get_attribute('outerHTML')}\n ------- FIN HTML --------\n\n\n")
					continue
		
				note.click() 
				time.sleep(ATTENTE_BOUTON)
				if nomComplet.strip() == '':
					prenom = ''
				else:
					prenom = nomComplet.split()[0]

				new_message = f"Bonjour {prenom},\n" + message

				textarea = elem.find_element_by_id('custom-message')
				textarea.clear() # On s'assure que c'est bien effacé
				textarea.send_keys(new_message)

				time.sleep(INPUT_ATTENTE)
				send.click()

				try: 
					self.insertName(username, message, nomComplet)
				except Exception as err: 
					self.ecrireLog("Probleme en base de donnee: " + str(err))
				else: self.ecrireLog(f"{username}: envoyé avec succès")

				time.sleep(MSG_INTERVAL)
			else:
				self.ecrireLog(f"{username}: deja envoyé PAR UN AUTRE BOT")


	def insertName(self, username, message, nom):
		db = sqlite3.connect("__bot.db")
		cursor = db.cursor()

		cursor.execute("""
			INSERT INTO Cible (utilisateur, message, nom_complet)
			VALUES (?, ?, ?)
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
		if args.get('suffix'):
			suffix = args.get('suffix')
		else: suffix = ''
		
		try:
			hauteur = self.chrome.execute_script("""
				return document.body.parentNode.scrollHeight
			""")

			self.chrome.set_window_size(1920, hauteur)
		except: 
			pass
		finally:
			body = self.chrome.find_element_by_tag_name("body")
			body.screenshot("log/images/"+self.logName+f"{suffix}.png")


	def ecrireLog(self, err):
		with open("log/"+self.logName+".txt", "a", encoding="utf-8") as logFile:
			logFile.write(str(err) + "\n")


	@classmethod
	def getName(self, username):
		_nom = username.split('-')
		nom = ""
		for __nom in _nom:
			if re.match(r"^[a-z'àáâãäåçèéêëìíîïðòóôõöùúûüýÿ]+$", __nom.lower()):
				nom = nom + " " +__nom.capitalize()
		return nom


if __name__ == "__main__":
	# initialiser un bot linkedin
	linkedin = Linkedin(PROXY)

	try:
		# se connecter
		linkedin.login(email, password)
	except Exception as err:
		print(err)
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
			print(err)
			linkedin.ecrireLog(err)
			linkedin.captureEcran()
			linkedin.chrome.close()
			exit()

		# envoyer message aux resultat
		try:
			linkedin.send_message_result(res, message)
		except Exception as err:
			print(err)
			linkedin.ecrireLog(err)
			linkedin.captureEcran()
			linkedin.chrome.close()
			exit()
		
		time.sleep(PAUSE_PAGE)

	linkedin.chrome.execute_script("""
		alert('Tâche terminé')
	""")