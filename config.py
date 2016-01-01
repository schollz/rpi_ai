from person import Person
import datetime
import keyring
import pickle

threshold = 100
sensitivity = 180
forceCapture = True
forceCaptureTime = 60 * 60 # Once an hour
filepath = "/home/pi/rpi_ai/video/"
filenamePrefix = "pgm"
fileType = "jpg"
saveWidth = 800 # File photo size settings
saveHeight = 600
diskSpaceToReserve = 40 * 1024 * 1024 # Keep 40 mb free on disk
CaptureDuration = 0
publicIP = keyring.get_password('my','public_ip')


gettingVoiceInput = 0
gettingVisualInput = 0
gettingStillImages = 0
gettingStillAudio = 0

blackLight = False
windowLamp = False

# How long to wait before stopping routine if nothing is happening
audioHangout = 60 # seconds
videoHangout = 300 # seconds
# How long to wait before starting up the routine again
timeTimeout = 0

# Force facial recognition
lookForFaces = 0

debugging = False

tasksLoaded = False


# make a list of class Person(s)
try:
	personList = pickle.load( open("ai_data/personlist.p","rb"))
except:
	personList = []
        personList.append(Person(name="Bob",job="Dish Washer"))
	pickle.dump(personList,open("ai_data/personlist.p","wb"))

# Need to set your own API codes 
#keyring.set_password('skybio','api_key','XX')
#keyring.set_password('skybio','api_secret','XX')
#keyring.set_password('skybio','app_name','XX')
#keyring.set_password('skybio','namespace','XX')
#keyring.set_password('wolfram','app_id','XX')
#keyring.set_password('msft_azure','api_secret','XX')
#keyring.set_password('msft_azure','api_client','XX')
#keyring.set_password('google','api_secret','XX')



