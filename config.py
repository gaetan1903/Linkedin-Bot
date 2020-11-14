email = "emc324@gmail.com"
password = "linkedin2020"


message = """Votre parcours est très intéressant bravo. J'aimerai vous compter parmi mon réseau. Si vous le souhaitez nous pouvons nous connecter . Je n'ai rien à proposer pour le moment mais qui sait ? peut-être plus tard aurions besoin de partager ?
 Je vous souhaite une bonne journée   """


# le mot clé à rechercher
mot_cle = "Responsable finance"


# Voci un exemple de Proxy , Metter en None ou False pour desactiver
# PROXY = "23.23.23.23:3128"
PROXY = None

'''
Mettre le chiifre representative dans le tableau 
pour la france : ville = ["105015875"]
Ile de france : ville = ["104246759"]
pour les deux par exemples: ville = '["105015875", "104246759"]'
'''
ville = '["104246759"]'


# nombres de pages à faire
# maximum 100
pages = 2


# interval de temps pour chaque message
MSG_INTERVAL = 5


# Attente après un get url 
# un loading page
ATTENTE_PAGE = 2


# Attente apres un click boutton
# bouton qui ne change pas de page
ATTENTE_BOUTON = 2


## Pause après avoir finis une page
PAUSE_PAGE = 3


## Delai d'attente entre les inputs
INPUT_ATTENTE = 1

