import config
import os
import pyaudio
from mouth_function import saySomething
from temporal_lobe import processInput
import time, datetime
import audioop

def getUserPermission(question):
	answer = 0
	saySomething(question,"en")
	response = getUsersVoice(2)
	if "yes" in response or "sure" in response or "okay" in response:
		answer = 1
	return answer
	
def listenToSurroundings(threadName):
	try:
		print "Started listening on thread %s" % threadName
		chunk = 1024
		
		if config.debugging:
			rms = []
			for i in range(0,10):
				p = pyaudio.PyAudio()
				stream = p.open(format=pyaudio.paInt16,channels=1,rate=44100,input=True,frames_per_buffer=chunk)
				data = stream.read(chunk)
				rmsTemp = audioop.rms(data,2)
				print rmsTemp
				rms.append(rmsTemp)
				rmsMean = numpy.mean(rms)
				rmsStd = numpy.std(rms)
				print rms
				stream.stop_stream()
				stream.close()
				p.terminate()
		
		volumeThreshold = 1050 # set after running the previous commands and looking at vtput
		print "Volume threshold set at %2.1f" % volumeThreshold 
		lastInterupt = datetime.datetime.now()
		
		while (1):
			if config.gettingStillImages and config.gettingStillAudio:
				pass
			elif config.gettingVisualInput:
				time.sleep(5)
			else:
				print "Starting listening stream"
				lastInterupt = datetime.datetime.now()
				config.gettingStillAudio = 0
				rmsTemp = 0
				p = pyaudio.PyAudio()
				stream = p.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=chunk)
				## listen to surroundings
				while rmsTemp < volumeThreshold and not config.gettingVisualInput:
					data = stream.read(chunk)
					rmsTemp = audioop.rms(data,2)
					timeDifference = datetime.datetime.now() - lastInterupt
					if timeDifference.total_seconds() > config.audioHangout:
						config.gettingStillAudio = 1
					if config.gettingStillAudio and config.gettingStillImages:
						break
				stream.stop_stream()
				stream.close()
				p.terminate()
				if not config.gettingVisualInput and not config.gettingStillAudio:
					config.timeTimeout = 0 # reset timeout
					config.gettingVoiceInput = 1
					output = getUsersVoice(5)
					processInput(output)
					config.gettingVoiceInput = 0
	except:
		import traceback
        print traceback.format_exc()

def getUsersVoice(speakingTime):
	os.system("mpg123 -a hw:1 sounds/computerbeep_61.mp3 > /dev/null 2>&1 ")
	os.system("arecord -D plughw:0 -f cd -t wav -d %d -r 16000 | flac - -f --best --sample-rate 16000 -o out.flac> /dev/null 2>&1 " % speakingTime)
	os.system("mpg123 -a hw:1 sounds/computerbeep_61.mp3 > /dev/null 2>&1 ")
	os.system("./parseVoiceText.sh ")
	output = ""
	with open('txt.out','r') as f:
		output = f.readline()
	print "output:"
	print output[1:-2]
	theOutput = output[1:-2]
	return theOutput