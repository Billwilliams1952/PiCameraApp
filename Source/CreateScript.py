PiCameraLoaded = True	
try:	
	import picamera
	from picamera import *
	import picamera.array
except ImportError:
	raise ImportError("You do not seem to have PiCamera installed")
	PiCameraLoaded = False
	
def OutputPythonScript ( camera ):
	# Open file
	# Loop through options and change
	pass
	

