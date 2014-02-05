import thread
import threading
import time
import random
import os
import audioop
from subprocess import Popen
import subprocess
import pyaudio
import numpy 
from chatterbotapi import ChatterBotFactory, ChatterBotType
import wolframalpha
import sys
import wikipedia
import re
import string
import pywapi
import urllib2,urllib
import json
from timeout import timeout
import requests
import datetime
import StringIO
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from face_client import FaceClient
import pickle
from ctypes import *
import math
#---------------------------------------------------------       
#				Global variables
#---------------------------------------------------------       


threshold = 25
sensitivity = 180
forceCapture = True
forceCaptureTime = 60 * 60 # Once an hour
filepath = "/home/pi/video"
filenamePrefix = "pgm"
fileType = "jpg"

saveWidth = 800 # File photo size settings
saveHeight = 600
diskSpaceToReserve = 40 * 1024 * 1024 # Keep 40 mb free on disk
CaptureDuration = 0


skybio_api_key = "90a8e8dccee545a79abb3f7890192927"
skybio_api_secret = "0f7314d73fd5465f9f21429902e66862"
skybio_application_name = "python-api"
skybio_namespace = "python"

wolframAppId = 'KU6R6J-KAUA83QJ73'
client = wolframalpha.Client(wolframAppId)

msftAzureSecret = 'w20+zMhSU49g+FGnpGzpiXSs+l2HCOMQT0dARyMK9EQ='
msftAzureClient = 'python-translator'

googleApi = 'AIzaSyDRpG-RuP7y8UN7WPOJoZA9d8m2LsvvEZs'

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

#---------------------------------------------------------       
#				Classes
#---------------------------------------------------------       


class Person(object):
	def __init__(self, name=None, job=None, greeting=None, lastSeen=None, gender=None):
		self.name = name
		self.job = job
		self.greeting = greeting
		self.lastSeen = lastSeen
		self.gender = gender
		print
		

		

#---------------------------------------------------------       
#				Functions
#---------------------------------------------------------       

#---------Motion detection and face recognition-----------
		
# Capture a small test image (for motion detection)
# Keep image in RAM until we need to do face recognition
def captureTestImage():
	command = "raspistill -w %s -h %s -t 1 -n -vf -e bmp -o -" % (100, 75)
	imageData = StringIO.StringIO()
	imageData.write(subprocess.check_output(command, shell=True))
	imageData.seek(0)
	im = Image.open(imageData)
	buffer = im.load()
	imageData.close()
	return im, buffer

# Probe Sky Biometry for Face recognization
def recognizeFace(theImg,filenameFull):
	font = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf", 14)
	theFileLocation =  "http://66.57.76.177/temp.jpg"
	client = FaceClient(skybio_api_key,skybio_api_secret)
	img = Image.open(theImg)
	width, height = img.size
	draw = ImageDraw.Draw(img)
	print theFileLocation
	photo = client.faces_recognize('all',theFileLocation, namespace = 'python')
	print photo
	# Number of people in photo
	numFaces = len(photo['photos'][0]['tags'])
	print "Detected " + str(numFaces) + " faces."
	textCaption = ""
	iii=0
	theSpeech = ""
	while iii<numFaces:
		for person in personList:
#		for j, person in enumerate(personList):
			try:
				theId = photo['photos'][0]['tags'][iii]['uids'][0]['uid']
				foundName = theId
				print "I see " + foundName
				xPos = width*(int(photo['photos'][0]['tags'][iii]['eye_right']['x']))/100
				yPos = height*(int(photo['photos'][0]['tags'][iii]['eye_right']['y']))/100
				if person.name in foundName: #and photo['photos'][0]['tags'][iii]['attributes']['gender']['value'] == person.gender:
					theSpeech = theSpeech + "%s" % person.greeting
					
					timeDifference = datetime.datetime.now() - person.lastSeen
					person.lastSeen = datetime.datetime.now()
					#personList[j].lastSeen = person.lastSeen
					days = math.floor(timeDifference.total_seconds() / 60 / 60 / 24)
					hours = math.floor(timeDifference.total_seconds() / 60 / 60	)	
					minutes = math.floor(timeDifference.total_seconds() / 60 )	
					if days > 0:
						theSpeech = theSpeech + "It's been %d days since I have seen you, %s. " % (days,person.name)
					elif hours > 4:
						theSpeech = theSpeech +  "It's been %d hours since I have seen you, %s. " % (hours,person.name)
					elif minutes > 0:
						theSpeech = theSpeech +  "It's been %d minutes since I have seen you, %s. " % (minutes,person.name)
					draw.text((xPos, yPos),person.name,(255,255,0),font=font)
					collection = ['eyes','sadness','mood','glasses']
					for x in collection:
						try:
							eyes = photo['photos'][0]['tags'][iii]['attributes'][x]['value']
							conf = photo['photos'][0]['tags'][iii]['attributes'][x]['confidence']
							if conf > 20:
								print " " + x + " = " + eyes
								yPos = yPos + 20
								draw.text((xPos, yPos)," " + x + ": " + eyes,(255,255,0),font=font)
								if x == 'mood':
									theSpeech = theSpeech + "Why are you " + eyes + "? "		
						except:
							print "No " + x
			except:
				print "Error locating face in person database."
		iii = iii + 1
	
	if len(theSpeech)>2: # proxy for if something happened
		img.save(filenameFull)
		img.save("/var/www/face.jpg")
		pickle.dump(personList, open("ai_data/personlist.p","wb") )
	return theSpeech

# Check whether a face has been seen recently
def seenAFaceInAwhile():
	# first check if anybody has been seen
	hasSeenSomeone = 0
	for person in personList:
		timeDifference = datetime.datetime.now() - person.lastSeen
		#personList[j].lastSeen = person.lastSeen
		days = round(timeDifference.total_seconds() / 60 / 60 / 24)
		hours = round(timeDifference.total_seconds() / 60 / 60	)	
		minutes = round(timeDifference.total_seconds() / 60 )	
		if minutes<10 and days < 1 and hours < 1:
			hasSeenSomeone = 1
	return hasSeenSomeone
	
# Save a full size image to disk
def saveImage(width, height, diskSpaceToReserve):
	global lookForFaces
	keepDiskSpaceFree(diskSpaceToReserve)
	time = datetime.datetime.now()
	filenameFull = "/home/pi/video/" + filenamePrefix + "-%04d%02d%02d%02d%02d%02d" % (time.year, time.month, time.day, time.hour, time.minute, time.second)+ "." + fileType
	
	# save onto webserver
	filename = "/var/www/temp.jpg"
	subprocess.call("sudo raspistill -w "+ str(saveWidth) +" -h "+ str(saveHeight) + " -t 1 -n -vf -e " + fileType + " -q 15 -o %s" % filename, shell=True)
	print "Captured image: %s" % filename

	theSpeech = recognizeFace(filename,filenameFull)
	if len(theSpeech)>2:
		print theSpeech
		saySomething(theSpeech,"en")
		lookForFaces = 0


# Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
	if (getFreeSpace() < bytesToReserve):
		for filename in sorted(os.listdir(".")):
			if filename.startswith(filenamePrefix) and filename.endswith("." + fileType):
				os.remove(filename)
				print "Deleted %s to avoid filling disk" % filename
				if (getFreeSpace() > bytesToReserve):
					return

# Get available disk space
def getFreeSpace():
	st = os.statvfs(".")
	du = st.f_bavail * st.f_frsize
	return du

# Get Google Tasks
def getTasksToday(dayBool):
	if dayBool==0:
		myTasks = ""
		numTasks = 0
		with open("tasks_today.txt") as f:
			for line in f:
				a=line.split(".")
				b=a[1].split(":")
				c=b[0].strip()
				if numTasks == 0:		
					myTasks = c
				else:
					myTasks = myTasks + ". Also, you have to " + c
				numTasks = numTasks+1
		if numTasks==0:
			return "You do not have to do anything next today! Relax, man!"
		else:
			return "You have " + str(numTasks) + " things to do today. You have to " + str(myTasks)
	if dayBool==1:
		myTasks = ""
		numTasks = 0
		with open("tasks_nextweek.txt") as f:
			for line in f:
				a=line.split(".")
				b=a[1].split(":")
				c=b[0].strip()
				if numTasks == 0:		
					myTasks = c
				else:
					myTasks = myTasks + ". Also, you have to " + c
				numTasks = numTasks+1
		if numTasks==0:
			return "You do not have to do anything next week! Relax, man!"
		else:
			return "You have " + str(numTasks) + " things to do next week. You have to " + str(myTasks)
		
# Translate text with Microsoft Translation
def translateText(s,language): 
	pattern = re.compile('([^\s\w]|_)+')
	b_string = re.sub(pattern, '', s.lower())
	phrase=" " + b_string + " "
	pattern = re.compile("\\b(in|chinese|italian|german|hebrew|say|translate|spanish|to)\\W", re.I)
	phrase_noise_removed = [pattern.sub("", phrase)] 
	text = phrase_noise_removed[0]
	print "translating " + text + " to " + language + "..."
	args = {
		'client_id': msftAzureClient,#your client id here
		'client_secret': msftAzureSecret,#your azure secret here
		'scope': 'http://api.microsofttranslator.com',
		'grant_type': 'client_credentials'
	    }
	    
	oauth_url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'
	oauth_junk = json.loads(requests.post(oauth_url,data=urllib.urlencode(args)).content)
	translation_args = {
		'text': text,
		'to': language,
		'from': 'en'
		}
	 
	headers={'Authorization': 'Bearer '+oauth_junk['access_token']}
	translation_url = 'http://api.microsofttranslator.com/V2/Ajax.svc/Translate?'
	translation_result = requests.get(translation_url+urllib.urlencode(translation_args),headers=headers)
	translation=translation_result.text[2:-1]
	print 'Translating ' + translation_args["text"]
	print 'Translation: ' + translation
	return translation

# Play song with VLC
def playSong(query):
	
	# get YouTube list
	pattern = re.compile('([^\s\w]|_)+')
	b_string = re.sub(pattern, '', query)
	phrase=b_string
	pattern = re.compile("\\b(some|play)\\W", re.I)
	query = [pattern.sub("", phrase)] 
	# get YouTube list
	query = query[0]
	print query
	#apiKey = 'AIzaSyBS82alyNuQJz1mhsGAZv2gbKh6_Nwaz5w'
	# travis' api key: #apiKey = 'AIzaSyCBd2oP__q4AHs6Cvzc-ktF4oNUVt3Bit4'
	url = "https://www.googleapis.com/youtube/v3/search?part=snippet&key="+googleApi+"&q="+urllib.quote_plus(query)+"&type=video"
	response = urllib2.urlopen(url)
	jsonResp = response.read()
	decoded = json.loads(jsonResp)
	#os.system('echo \''+url+'\' > url.txt') #for debugging
	url = 'http://youtube.com/watch?v=' + decoded['items'][0]['id']['videoId']
	theSongName = decoded['items'][0]['snippet']['title']
	pattern = re.compile("([^a-zA-Z\d\s:,.']|_)+")
	theSongName = re.sub(pattern, '', theSongName)
	#for x in range(1,len(decoded['items'])):
	#url = url + ' ' + 'http://youtube.com/watch?v=' + decoded['items'][x]['id']['videoId']
	permission = getUserPermission("Do you want to hear " + theSongName)
	if permission:
		vlc = 'cvlc --no-video --volume 270 -A alsa,none --alsa-audio-device hw:1' + ' ' + url + ' --play-and-exit &'
		print url
		os.system(vlc)
		print "started music.."
		return "Sure I'll play " + theSongName
	else:
		return "Okay, I will play nothing."

def getUserPermission(question):
	answer = 0
	saySomething(question,"en")
	response = getUsersVoice(2)
	if "yes" in response or "sure" in response or "okay" in response:
		answer = 1
	return answer


	
def getAIresponse(s):
	try: 
		return getAIresponse2(s)
	except:
		return "Sorry, I can't do that."

#@timeout(8)
def getAIresponse2(s):
	factory = ChatterBotFactory()
	bot2 = factory.create(ChatterBotType.CLEVERBOT)
	bot2session = bot2.create_session()
	response = bot2session.think(s)
	return response

def getInput(threadName):
	while 1:
		theInput = raw_input()
		processInput(theInput)

	
def innerStimulus(threadName):
	random.seed()
	print "%s started" % threadName
	while (1):
		time.sleep(1)
		if (random.random() < 0.05):
			rsp =  getAIresponse(" ")
			print rsp
			saySomething(rsp)

def wolframLookUp(a_string):
	pattern = re.compile('([^\s\w]|_)+')
	b_string = re.sub(pattern, '', a_string)
	phrase=b_string
	pattern = re.compile("\\b(what|is)\\W", re.I)
	phrase_noise_removed = [pattern.sub("", phrase)] 
	try:
		res= client.query(a_string)
		return next(res.results).text
	except:
		return getAIresponse(a_string)

#@timeout(5)
def wikipediaLookUp(a_string,num_sentences):
	print a_string
	pattern = re.compile('([^\s\w]|_)+')
	b_string = re.sub(pattern, '', a_string)
	phrase=b_string
	print phrase
	pattern = re.compile("\\b(lot|lots|a|an|who|can|you|what|is|info|somethings|whats|have|i|something|to|know|like|Id|information|about|tell|me)\\W", re.I)
	phrase_noise_removed = [pattern.sub("", phrase)] 
	print phrase_noise_removed[0]
	a = wikipedia.search(phrase_noise_removed[0])
	print a[0]
	the_summary = (wikipedia.summary(a[0], sentences=num_sentences))
	print the_summary
	return the_summary	

		
def saySomething(txt,language):
	#use alsamixer to check which is which (is 0 recording? or is 1?)
	#os.system("espeak -ven+f3 -k5 -s150 '" + txt + "'")
	print "speaking " + language
	words = txt.split()
	numWords = len(words)
	sentences = ""
	curSentence = 0
	curCharacters = 0
	curWord = 0
	for word in words:
		if curCharacters+len(word)+1<100:
			sentences = sentences+'%20'+word
		else:
			curSentence = curSentence + 1
			sentences = sentences + "111" + word
			curCharacters = 0
		curCharacters = curCharacters + len(word)+1
		curWord = curWord + 1
	
	feedTxt = sentences.split("111")
	for sentence in feedTxt:
		sentence = sentence.replace("'","%27")
		print sentence
		os.system("mpg123 -a hw:1 -q 'http://translate.google.com/translate_tts?tl="+language+"&q=" + sentence + "'")


def listenToSurroundings(threadName):
	try:
		global gettingVoiceInput
		global gettingVisualInput
		global gettingStillImages
		global gettingStillAudio
		global timeTimeout
		
		print "Started listening on thread %s" % threadName
		chunk = 1024
		
		## Keep this code for debugging
		#rms = []
		#for i in range(0,10):
	#		p = pyaudio.PyAudio()
	#		stream = p.open(format=pyaudio.paInt16,channels=1,rate=44100,input=True,frames_per_buffer=chunk)
	#		data = stream.read(chunk)
	#		rmsTemp = audioop.rms(data,2)
	#		print rmsTemp
		#	rms.append(rmsTemp)
		#   rmsMean = numpy.mean(rms)
		#   rmsStd = numpy.std(rms)
		#   print rms
		#	stream.stop_stream()
	#		stream.close()
	#		p.terminate()
		
		volumeThreshold = 1050 # set after running the previous commands and looking at vtput
		print "Volume threshold set at %2.1f" % volumeThreshold 
		lastInterupt = datetime.datetime.now()
		
		while (1):
			if gettingStillImages and gettingStillAudio:
				pass
#				if timeTimeout == 0:
#					timeTimeout = 10 
#				else:
#					timeTimeout += timeTimeout
#				print "No one is around, shutting ears for %d seconds" % timeTimeout
#				time.sleep(timeTimeout)
#				gettingStillAudio = 0
			elif gettingVisualInput:
				time.sleep(5)
			else:
				print "Starting listening stream"
				lastInterupt = datetime.datetime.now()
				gettingStillAudio = 0
				rmsTemp = 0
				p = pyaudio.PyAudio()
				stream = p.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=chunk)
				## listen to surroundings
				while rmsTemp < volumeThreshold and not gettingVisualInput:
					data = stream.read(chunk)
					rmsTemp = audioop.rms(data,2)
					timeDifference = datetime.datetime.now() - lastInterupt
					if timeDifference.total_seconds() > audioHangout:
						gettingStillAudio = 1
					if gettingStillAudio and gettingStillImages:
						break
				stream.stop_stream()
				stream.close()
				p.terminate()
				if not gettingVisualInput and not gettingStillAudio:
					timeTimeout = 0 # reset timeout
					gettingVoiceInput = 1
					output = getUsersVoice(5)
					processInput(output)
					gettingVoiceInput = 0
	except:
		import traceback
        print traceback.format_exc()

def getUsersVoice(speakingTime):
	os.system("mpg123 -a hw:1 sounds/computerbeep_$(((RANDOM % 15 ) + 60)).mp3 > /dev/null 2>&1 ")
	os.system("arecord -D plughw:0 -f cd -t wav -d %d -r 16000 | flac - -f --best --sample-rate 16000 -o out.flac> /dev/null 2>&1 " % speakingTime)
	os.system("mpg123 -a hw:1 sounds/computerbeep_$(((RANDOM % 15 ) + 60)).mp3 > /dev/null 2>&1 ")
	os.system("./parseVoiceText.sh ")
	output = ""
	with open('txt.out','r') as f:
		output = f.readline()
	print "output:"
	print output[1:-2]
	theOutput = output[1:-2]
	return theOutput
		
def lookAtSurroundings(threadName):
	global gettingVoiceInput
	global gettingVisualInput
	global gettingStillImages
	global gettingStillAudio
	global timeTimeout
	global lookForFaces
	
	motionDetectedLast = datetime.datetime.now()
	motionDetectedNow = datetime.datetime.now()
	print "Started listening on thread %s" % threadName
	## look at surroundings
	# Get first image
	image1, buffer1 = captureTestImage()
	# Reset last capture time
	lastCapture = time.time()
	while (1):
		# check if CPU intensive processes are running
		output = os.popen("pgrep vlc").read()
		isRunning = 0
		if len(output) > 0:
			isRunning = 1
#		if gettingStillImages and gettingStillAudio:
#			if timeTimeout == 0:
#				timeTimeout = 10 
#			print "No one is around, closing eyes for %d seconds" % timeTimeout
#			time.sleep(timeTimeout)
#			gettingStillImages = 0
#			motionDetectedLast = datetime.datetime.now()
		if gettingVoiceInput==1:
			time.sleep(6)
		elif isRunning:
			time.sleep(20)
		else:
			# Get comparison image
			image2, buffer2 = captureTestImage()
			pixelSum =  0
			numCountedPixels = 0
			motionHasBeenDetected = False
			# Count changed pixels
			changedPixels = 0
			for x in xrange(0, 100):
				# Scan one line of image then check sensitivity for movement
				for y in xrange(0, 75):
					# Just check green channel as it's the highest quality channel
					pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
					pixelSum += buffer1[x,y][1]
					numCountedPixels += 1
					if pixdiff > threshold:
						changedPixels += 1
				# Changed logic - If movement sensitivity exceeded then
				# Save image and Exit before full image scan complete
				if changedPixels > sensitivity:   
					lastCapture = time.time()
					print "Motion detected! changedPixels > sensitivity (" + str(changedPixels) + " > " + str(sensitivity) + ")"
					motionDetectedLast = datetime.datetime.now()
					motionHasBeenDetected = True
					timeTimeout = 0 # reset timeout
					if not seenAFaceInAwhile():
						gettingVisualInput = 1
						saveImage(saveWidth, saveHeight, diskSpaceToReserve) # face detection
						gettingVisualInput = 0
					break
				continue	
			print "Changed pixels : " + str(changedPixels)
			if (numCountedPixels>500):
				lightChange = pixelSum / numCountedPixels
				print "Pixel sum : %2.1f" % lightChange
				if (lightChange < 5):
					windowLamp = False
					blackLight = False
					os.system("echo 'rf a1 on' | nc localhost 1099")
					os.system("echo 'rf c1 on' | nc localhost 1099")
				elif (lightChange > 5) and (lightChange <= 14):
					blackLight = False
					windowLamp = True
					os.system("echo 'rf a1 on' | nc localhost 1099")
				elif (lightChange > 14) and (lightChange <= 50):
					blackLight = True
					windowLamp = False
					os.system("echo 'rf c1 on' | nc localhost 1099")
				else:
					blackLight = True
					windowLamp = True				
				print blackLight
				print windowLamp
			# Check force capture
			if forceCapture:
				if time.time() - lastCapture > forceCaptureTime:
					changedPixels = sensitivity + 1
			# Swap comparison buffers
			image1  = image2
			buffer1 = buffer2
			timeDifference = datetime.datetime.now() - motionDetectedLast
			minutes = round(timeDifference.total_seconds() / 60 )	
			if timeDifference.total_seconds() > videoHangout:
				gettingStillImages = 1
			else:
				gettingStillImages = 0
			if lookForFaces:
				gettingVisualInput = 1
				saveImage(saveWidth, saveHeight, diskSpaceToReserve) # face detection
				gettingVisualInput = 0

				
def processInput(s):
	global gettingVoiceInput
	global gettingVisualInput
	global gettingStillImages
	global gettingStillAudio
	global timeTimeout
	global lookForFaces
	s = s.lower()
	print "You entered %s" % (s)
	rsp = ""
	language="en"
	if "spanish" in s:
		language = 'es'
		try:
			rsp = translateText(s,language)
		except:
			language = 'en'
			rsp = 'Language services not accessible at this time'
	elif "german" in s:
		language = 'de'
		try:
			rsp = translateText(s,language)
		except:
			language = 'en'
			rsp = 'Language services not accessible at this time'
	elif "italian" in s:
		language = 'it'
		try:
			rsp = translateText(s,language)
		except:
			language = 'en'
			rsp = 'Language services not accessible at this time'
	elif "weather" in s:
		result = pywapi.get_weather_from_noaa('KRDU') # RDU
		rsp = 'It is currently ' + str(int(float(result['temp_f']))) + ' degrees and ' + result['weather']
	elif ("i doing" in s) or (("to do" in s) and ("have" in s or "need" in s)):
		if "tomorrow" in s or "week" in s or "next" in s:
			rsp = getTasksToday(1)
			print "Got response " + rsp
		else:
			rsp = getTasksToday(0)
			print "Got response " + rsp
	elif "play" in s:
		rsp = playSong(s)
	elif "music" in s:
		if "stop" in s:
			os.system('pkill vlc')
		elif "cancel" in s:
			os.system('pkill vlc')
		elif "kill" in s:
			os.system('pkill vlc')
		elif "close" in s:
			os.system('pkill vlc')
	elif "what is the" in s or "what's the" in s:	
		rsp = wolframLookUp(s)
	elif "how many" in s:
		rsp = wolframLookUp(s)
	elif "tell me" in s:
		if "joke" in s:
			rsp = wolframLookUp('tell me a joke')			
		elif "funny" in s:
			rsp = wolframLookUp('tell me a joke')
		elif "lot" in s:
			try:
				rsp = wikipediaLookUp(s,2)
			except:
				try:
					rsp = wikipediaLookUp(s,2)
				except:
					rsp = "I am sorry, I can not access that information."
		else:
			try:
				rsp = wikipediaLookUp(s,2)
			except:
				try:
					rsp = wikipediaLookUp(s,2)
				except:
					rsp = "I am sorry, I can not access that information."
	elif "do you know" in s:
		try:
			rsp = wikipediaLookUp(s,2)
		except:
			try:
				rsp = wikipediaLookUp(s,2)
			except:
				rsp = "I am sorry, I can not access that information."
	elif "who am i" in s or "who do you see" in s or "do you recognize" in s or "do you know me" in s:
		lookForFaces = 1
		rsp = "Let me see you and think."
		gettingStillImages = 0
	elif "off" in s and "light" in s:
		os.system("echo 'rf a1 off' | nc localhost 1099")
		os.system("echo 'rf c1 off' | nc localhost 1099")
		os.system("echo 'rf a1 off' | nc localhost 1099")
		os.system("echo 'rf c1 off' | nc localhost 1099")
		rsp = "Turning off the lights"
	elif "on" in s and "light" in s:
		os.system("echo 'rf a1 on' | nc localhost 1099")
		os.system("echo 'rf c1 on' | nc localhost 1099")
		os.system("echo 'rf a1 on' | nc localhost 1099")
		os.system("echo 'rf c1 on' | nc localhost 1099")
		rsp = "Turning on the lights"
	elif "who" in s:
		try:
			rsp = wikipediaLookUp(s,1)
		except:
			try:
				rsp = wikipediaLookUp(s,1)
			except:
				rsp = "I am sorry, I can not access that information."
	elif "shut" in s and "down" in s:
		saySomething("Shutting the computer down","en")
		os.system("sudo shutdown now &")
	else:
		rsp = getAIresponse(s)
	print rsp

	pattern = re.compile("([^a-zA-Z\d\s:,.']|_)+")
	rsp = re.sub(pattern, '', rsp)
	print rsp + " in " + language
	saySomething(rsp,language)
		
#os.system("python myTasks2.py -l 'Zack-todo' > current_tasks.txt")
## today
#os.system("rm tasks_today.txt")
#os.system("touch tasks_today.txt")
#today = datetime.date.today()
#todayStr = today.strftime("%Y-%m-%d")
#os.system("cat current_tasks.txt | grep " + todayStr + " > tasks_today.txt")
#os.system("rm tasks_nextweek.txt")
#os.system("touch tasks_nextweek.txt")
#for x in range(1,7):
#	today = datetime.date.today()+datetime.timedelta(days=x)
#	todayStr = today.strftime("%Y-%m-%d")
#	os.system("cat current_tasks.txt | grep " + todayStr + " >> tasks_nextweek.txt")

	
# make a list of class Person(s)
try:
	personList = pickle.load( open("ai_data/personlist.p","rb"))
except:
	personList = []
	personList.append(Person("zack","pee h dee student","hi zack. ",datetime.datetime(2014,1,28,12,0,0),"male"))
	personList.append(Person("ashley","law student","it is lovely to see you ashley. ",datetime.datetime(2014,1,27,0,0,0),"female"))

#saySomething('Hello, I am an Ay Eye','en')


try:
	thread.start_new_thread( listenToSurroundings,("AudioCortex",))
	thread.start_new_thread( lookAtSurroundings,("VisualCortex",))
#	thread.start_new_thread( listenToMic,("UserVoiceEvent",))
except:
	print "Error, unable to start thread."


while 1:
	pass




