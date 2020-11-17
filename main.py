import time
from linkedin import Linkedin
from config import *




# initialiser un bot linkedin
linkedin = Linkedin(**CONFIG)

try:
	# se connecter
	linkedin.login(email, password)
except Exception as err:
	print(err)
	linkedin.ecrireLog(err)
	linkedin.captureEcran()
	linkedin.chrome.close()
	exit()


linkedin.cancelInvitation()
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
		continue
	else:
		# si aucun bouton connecter sur la page
		if len(res)==0:
			print(f"Aucun boutton se connecter sur la page {page}")
			continue

	# envoyer message aux resultat
	try:
		linkedin.send_message_result(res, message)
	except Exception as err:
		print(err)
		linkedin.ecrireLog(err)
		linkedin.captureEcran()
		linkedin.chrome.close()
		exit()
	
	time.sleep(linkedin.PAUSE_PAGE)

linkedin.chrome.execute_script("""
	alert('Tâche terminé')
""")