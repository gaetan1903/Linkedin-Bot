email = "emc324@gmail.com"
password = "linkedin2020"

message = """Votre parcours est très intéressant bravo. J'aimerai vous compter parmi mon réseau. Si vous le souhaitez nous pouvons nous connecter . Je n'ai rien à proposer pour le moment mais qui sait ? peut-être plus tard aurions besoin de partager ?
 Je vous souhaite une bonne journée   """

# le mot clé à rechercher
mot_cle = "Medecin"

# nombres de pages à faire
# maximum 100
pages = 2

'''
Mettre le chiffre representative dans le tableau 
pour la france : ville = ["105015875"]
Ile de france : ville = ["104246759"]
pour les deux par exemples: ville = '["105015875", "104246759"]'
'''
ville = '["104246759"]'

# limit d'invitation pour aller faire la suppression 
limitinvitation = 200 

# llimit de page d'invitation
invitationPage = 1

# ------------------------------------------------------------#
#                  DEBUT CONFIG OPTIONNEL					  #
# ------------------------------------------------------------#
CONFIG = {}
'''
Voci un exemple de Proxy , Metter en None ou False pour desactiver
PROXY = "23.23.23.23:3128 
'''
CONFIG['PROXY'] = None

# interval de temps pour chaque message
CONFIG['MSG_INTERVAL'] = 3

# Attente après un get url 
# un loading page
CONFIG['ATTENTE_PAGE'] = 2

# Attente apres un click boutton
# bouton qui ne change pas de page
CONFIG['ATTENTE_BOUTON'] = 2

## Pause après avoir finis une page
CONFIG['PAUSE_PAGE'] = 3

## Delai d'attente entre les inputs
CONFIG['INPUT_ATTENTE'] = 1

