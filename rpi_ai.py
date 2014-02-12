import config
from visual_cortex import lookAtSurroundings
from audio_cortex import listenToSurroundings
import thread

try:
	thread.start_new_thread( listenToSurroundings,("AudioCortex",))
	thread.start_new_thread( lookAtSurroundings,("VisualCortex",))
except:
	print "Error, unable to start thread."

while 1:
	pass




