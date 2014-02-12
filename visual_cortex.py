import config
import datetime 
import StringIO
import subprocess
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from face_client import FaceClient
from person import Person
from mouth_function import saySomething
import pickle
import time
import os
import keyring
import sys
import math

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
	theFileLocation =  "http://" + config.publicIP + "/temp.jpg"
	client = FaceClient(keyring.get_password('skybio','api_key'),keyring.get_password('skybio','api_secret'))
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
		for person in config.personList:
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
					draw.text((0, 0),time.strftime("%c"),(255,255,0),font=font)
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
				print "Unexpected error:", sys.exc_info()[0]
				raise
		iii = iii + 1
	
	if len(theSpeech)>2: # proxy for if something happened
		img.save(filenameFull)
		img.save("/var/www/face.jpg")
		pickle.dump(config.personList, open("ai_data/personlist.p","wb") )
	return theSpeech

# Check whether a face has been seen recently
def seenAFaceInAwhile():
	# first check if anybody has been seen
	hasSeenSomeone = 0
	for person in config.personList:
		timeDifference = datetime.datetime.now() - person.lastSeen
		#personList[j].lastSeen = person.lastSeen
		days = round(timeDifference.total_seconds() / 60 / 60 / 24)
		hours = round(timeDifference.total_seconds() / 60 / 60	)	
		minutes = round(timeDifference.total_seconds() / 60 )	
		if minutes<10 and days < 1 and hours < 1:
			hasSeenSomeone = 1
	return hasSeenSomeone
	
# Save a full size image to disk
def saveImage():
	keepDiskSpaceFree(config.diskSpaceToReserve)
	time = datetime.datetime.now()
	filenameFull = config.filepath + config.filenamePrefix + "-%04d%02d%02d%02d%02d%02d" % (time.year, time.month, time.day, time.hour, time.minute, time.second)+ "." + config.fileType
	
	# save onto webserver
	filename = "/var/www/temp.jpg"
	subprocess.call("sudo raspistill -w "+ str(config.saveWidth) +" -h "+ str(config.saveHeight) + " -t 1 -n -vf -e " + config.fileType + " -q 15 -o %s" % filename, shell=True)
	print "Captured image: %s" % filename

	theSpeech = recognizeFace(filename,filenameFull)
	if len(theSpeech)>2:
		print theSpeech
		saySomething(theSpeech,"en")
		config.lookForFaces = 0


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

def lookAtSurroundings(threadName):
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
#		if config.gettingStillImages and config.gettingStillAudio:
#			if config.timeTimeout == 0:
#				config.timeTimeout = 10 
#			print "No one is around, closing eyes for %d seconds" % config.timeTimeout
#			time.sleep(config.timeTimeout)
#			config.gettingStillImages = 0
#			motionDetectedLast = datetime.datetime.now()
		if config.gettingVoiceInput==1:
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
					if pixdiff > config.threshold:
						changedPixels += 1
				# Changed logic - If movement sensitivity exceeded then
				# Save image and Exit before full image scan complete
				if changedPixels > config.sensitivity:   
					lastCapture = time.time()
					print "Motion detected! changedPixels > sensitivity (" + str(changedPixels) + " > " + str(config.sensitivity) + ")"
					motionDetectedLast = datetime.datetime.now()
					motionHasBeenDetected = True
					config.timeTimeout = 0 # reset timeout
					if not seenAFaceInAwhile():
						config.gettingVisualInput = 1
						saveImage() # face detection
						config.gettingVisualInput = 0
					break
				continue	
			print "Changed pixels : " + str(changedPixels)
			if (numCountedPixels>500):
				lightChange = pixelSum / numCountedPixels
				print "Pixel sum : %2.1f" % lightChange
				if (lightChange < 5):
					os.system("echo 'rf a1 on' | nc localhost 1099")
					os.system("echo 'rf c1 on' | nc localhost 1099")
			# Check force capture
			if config.forceCapture:
				if time.time() - lastCapture > config.forceCaptureTime:
					changedPixels = config.sensitivity + 1
			# Swap comparison buffers
			image1  = image2
			buffer1 = buffer2
			timeDifference = datetime.datetime.now() - motionDetectedLast
			minutes = round(timeDifference.total_seconds() / 60 )	
			if timeDifference.total_seconds() > config.videoHangout:
				config.gettingStillImages = 1
			else:
				config.gettingStillImages = 0
			if config.lookForFaces:
				config.gettingVisualInput = 1
				saveImage() # face detection
				config.gettingVisualInput = 0