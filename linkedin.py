import os, re, time, datetime, urllib.parse
import mysql.connector 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from config import database



class Linkedin:
	def __init__(self, **kwargs):
		self.kwargs = kwargs
		self._config()
		self._initDb()
		self.logName = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
		# create file 
		with open("log/"+self.logName+".txt", "w"): pass
		self.sendCount = 0


	def _config(self):
		self.PROXY = self.kwargs.get("PROXY") \
			if self.kwargs.get("PROXY") else None
		self.MSG_INTERVAL = self.kwargs.get("MSG_INTERVAL") \
			if self.kwargs.get("MSG_INTERVAL") else 5
		self.ATTENTE_PAGE = self.kwargs.get("ATTENTE_PAGE") \
			if self.kwargs.get("ATTENTE_PAGE") else 2
		self.ATTENTE_BOUTON = self.kwargs.get("ATTENTE_BOUTON") \
			if self.kwargs.get("ATTENTE_BOUTON") else 2
		self.PAUSE_PAGE = self.kwargs.get("PAUSE_PAGE") \
			if self.kwargs.get("PAUSE_PAGE") else 3
		self.INPUT_ATTENTE = self.kwargs.get("INPUT_ATTENTE") \
			if self.kwargs.get("INPUT_ATTENTE") else 1
		self.maxInvitations = self.kwargs.get('maxInvitations') \
			if self.kwargs.get('maxInvitations') else 200 

		# CREATION DOSSIER DE LOG
		if not os.path.isdir('log'):
			os.mkdir('log')
		if not os.path.isdir('log/images'):
			os.mkdir('log/images')

		options = Options()
		# AJOUT D'ADRESSES PROXY SI DEFINIT
		if self.PROXY: 
			options.add_argument(f'--proxy-server={self.PROXY}')
			options.add_argument('--disable-gpu')
		self.chrome = webdriver.Chrome(os.path.abspath('driver\\chromedriver.exe'), options=options)
		self.chrome.maximize_window()


	def _initDb(self):
		db = mysql.connector.connect(**database)
		cursor = db.cursor()

		cursor.execute("""
			CREATE TABLE IF NOT EXISTS`Cible` (
				`id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
				`utilisateur` VARCHAR(50),
				`nom_complet` VARCHAR(100),
				`message` TEXT,
				`invitation` TINYINT NOT NULL DEFAULT 1,
				 PRIMARY KEY (`id`), INDEX `utilisateur` (`utilisateur`)
			)
		""")

		db.commit()
		db.close()



	def login(self, email, password):
		self.chrome.get('https://www.linkedin.com/login/fr?fromSignIn=true')
		time.sleep(self.ATTENTE_PAGE)
		# ciblage des champs necessaire
		userChamp = self.chrome.find_element_by_id('username')
		passwordChamp = self.chrome.find_element_by_id('password')
		loginBouton = self.chrome.find_element_by_xpath("//button[@type='submit']")
	
		userChamp.send_keys(email)
		time.sleep(self.INPUT_ATTENTE)

		passwordChamp.send_keys(password)
		time.sleep(self.INPUT_ATTENTE)

		loginBouton.click()


	def recherche(self, query, **filtre):
		if self.sendCount >= self.maxInvitations:
			self.chrome.close()
			exit()
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
		time.sleep(self.ATTENTE_PAGE)

		section = self.chrome.find_element_by_xpath("//ul[contains(@class, 'search-result')]")
		try:
			# verifier s'il y a dispo
			verifBut = section.find_elements_by_xpath('//li//button[text()="Se connecter"]')
		except: 
			# si pas dispo, vide alors
			return []

		# attendre que la page se charge completement
		while not self.page_has_loaded():
			pass
		return section.find_elements_by_tag_name("li")
		


	def send_message_result(self, elements, message):
		for block in elements:
			if self.sendCount >= self.maxInvitations:
				print("Nombre d'invitation atteint")
				break
			try:
				link = block.find_element_by_tag_name('a')
			except: 
				self.ecrireLog(f"la balise a n'est pas trouvé dans:\n------- DEBUT HTML -------- {block.get_attribute('outerHTML')}\n ------- FIN HTML --------\n\n\n")
				continue
			
			username = self.extractUsername(link.get_property('href'))
			if username.startswith('?'):
				continue

			try:	
				nomComplet = block.find_element_by_tag_name("h3").find_element_by_class_name("actor-name").text
			except: 
				self.ecrireLog(f"la balise h3 n'est pas trouvé dans:\n------- DEBUT HTML -------- {block.get_attribute('outerHTML')}\n ------- FIN HTML --------\n\n\n")
				nomComplet = self.getName(username)
			else:
				if nomComplet.strip() == '':
					nomComplet = self.getName(username)

			print(f"----> {nomComplet}")
			try:
				btn = WebDriverWait(block, 3).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
			except Exception as err:
				self.ecrireLog(f"{nomComplet}: Ne peut pas etre envoyée de message\n------- DEBUT HTML -------- {block.get_attribute('outerHTML')}\n ------- FIN HTML --------\n\n\n")
				block.screenshot(f"log/images/{self.logName}_{nomComplet}.png")
				continue

			if btn.text.strip() != 'Se connecter': 
				print("le bouton n'est pas 'Se connecter' :", btn.text)
				continue 

			if self.verifName(username, message):
				try:
					btn.click()
				except Exception as err:
					self.ecrireLog(f"{username} - Bouton Non cliquable:\n {err}\n {btn.get_attribute('outerHTML')}")
					continue 

				time.sleep(self.ATTENTE_BOUTON)

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
		
				try:
					note.click()
				except Exception as err:
					self.chrome.find_element_by_tag_name('body').click()
					continue 

				time.sleep(self.ATTENTE_BOUTON)

				try:
					prenom = elem.find_element_by_id("send-invite-modal").text
					prenom = prenom.replace("Invitez", "").replace("à rejoindre votre réseau", "").strip()
				except Exception as err:
					print(err)
					prenom = ''

				new_message = f"Bonjour {prenom},\n" + message

				textarea = elem.find_element_by_id('custom-message')
				textarea.clear() # On s'assure que c'est bien effacé
				textarea.send_keys(new_message)

				time.sleep(self.INPUT_ATTENTE)
				try:
					send.click()
				except Exception as err:
					self.chrome.find_element_by_tag_name('body').click()
					continue

				try: 
					self.insertName(username, message, nomComplet)
				except Exception as err: 
					self.ecrireLog("Probleme en base de donnee: " + str(err))
				else:
					self.ecrireLog(f"{username}: envoyé avec succès")
					self.sendCount += 1 

				time.sleep(self.MSG_INTERVAL)
			else:
				self.ecrireLog(f"{username}: deja envoyé PAR UN AUTRE BOT")


	def insertName(self, username, message, nom):
		db = mysql.connector.connect(**database)
		cursor = db.cursor()

		cursor.execute("""
			INSERT INTO Cible (utilisateur, message, nom_complet)
			VALUES (%s, %s, %s)
		""", (username, message, nom))
		db.commit()
		db.close()


	def verifName(self, username, message):
		db = mysql.connector.connect(**database)
		cursor = db.cursor()
		cursor.execute("""
			SELECT 1
			FROM Cible 
			WHERE utilisateur = %s
			AND message = %s
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
				nom += " " +__nom.capitalize()
		return nom


	def invitationStatus(self, username):
		db = mysql.connector.connect(**database)
		cursor = db.cursor()
		cursor.execute("""
			UPDATE Cible SET invitation = 0
			WHERE utilisateur = %s
		""", (username,))

		db.commit()
		db.close()


	@classmethod
	def extractUsername(self, url):
		# extraction du nom d'utilisateur du lien 
		tmpuser = url.split('/')
		while tmpuser[-1].strip() == '':
			tmpuser = tmpuser[:-1]
		return urllib.parse.unquote(tmpuser[-1]).strip()


	def page_has_loaded(self):
		page_state = self.chrome.execute_script('return document.readyState;')
		return page_state == 'complete'


	def cancelInvitation(self, page):
		def retirer():
			time.sleep(self.ATTENTE_BOUTON)
			elem = self.chrome.switch_to.active_element
			btn = elem.find_element_by_xpath("//button//span[text()='Retirer']/parent::button")
			try:
				b_Id = btn.get_attribute('id')
				self.chrome.execute_script(f"document.getElementById('{b_Id}').click();")
			except Exception as err:
				print(err)
				self.ecrireLog(err)
			else:
				print(f"invitation {username} annulée")
				self.invitationStatus(username)
			finally:
				self.chrome.find_element_by_tag_name('body').click()


		self.chrome.get('https://www.linkedin.com/mynetwork/invitation-manager/sent/')
		time.sleep(self.ATTENTE_PAGE)

		try: 
			lastPage = self.chrome.find_element_by_xpath("//ul[contains(@class, 'number')]//li[last()]").text
			if not re.match(r'[0-9]', lastPage.strip()):
				raise Exception
		except:
			lastPage = "1"
		finally:
			lastPage = int(lastPage)

		while page <= lastPage :
			try:
				self.chrome.get(f'https://www.linkedin.com/mynetwork/invitation-manager/sent/?page={page}')
			except Exception as err:
				print(err)
				self.ecrireLog(err)
				self.captureEcran("page_invitation")
			finally:
				page = page + 1 

			time.sleep(self.ATTENTE_PAGE)
 
			try:
				pr = self.chrome.find_elements_by_xpath("//ul[contains(@class, 'invitation')]//li")
			except Exception as err:
				print(err)
				self.ecrireLog(err)
				pr = []

			for block in pr:

				try:
					link = block.find_element_by_tag_name("a")
					username = self.extractUsername(link.get_attribute('href'))
					bouton = block.find_element_by_xpath("//button//span[text()='Retirer']/parent::button")
					bouton.click()
					retirer()
				except Exception as err:
					print(err)
					self.chrome.find_element_by_tag_name('body').click()

				time.sleep(self.MSG_INTERVAL)
		print("Tous les pages terminés")
	

	def verifInvitation(self, nombre):
		db = mysql.connector.connect(**database)
		cursor = db.cursor()
		cursor.execute("""
			SELECT count(id) FROM Cible
			WHERE invitation = 1
		""")
		res = cursor.fetchone()
		db.close()
		return res[0] >= nombre \
			if res[0] else False
		




			

