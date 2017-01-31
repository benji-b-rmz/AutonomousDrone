# Alexander Barrick, Benjamin Ramirez
# Using opencv3.1.0 from detect.py 
#using the PS_DRONE api found at:   http://www.playsheep.de/drone/ functions
import time, sys
import ps_drone
import cv2                                
import numpy as np
from detect import detectColor

MIN_SIZE = 30
MAX_SIZE = 250
GOAL_RADIUS = 65
INTERVAL = 250
T_GAIN = 0.3
F_GAIN = 0.06
ARRAYSIZE = 30

LISTOFVALUES = [0] * ARRAYSIZE
VALUESFORYAW = [320] * ARRAYSIZE
position_in_array = 0
average = 0
average_x_location = 0

drone = ps_drone.Drone()                                     # Start using drone
drone.startup()                                              # Connects to drone and starts subprocesses

drone.reset()                                                # Sets drone's status to good (LEDs turn green when red)
while (drone.getBattery()[0] == -1):      time.sleep(0.1)    # Waits until drone has done its reset
print "Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1])   # Gives a battery-status
drone.useDemoMode(True)                                      

##### Mainprogram begin #####
drone.setConfigAllID()                                       
drone.sdVideo()                                              
drone.frontCam()                                             # Choose front view
time.sleep(2)
cap = cv2.VideoCapture('tcp://192.168.1.1:5555')
time.sleep(2)

##### FLIGHT #########
drone.takeoff()                # Drone starts
drone.trim()
time.sleep(4)
#time.sleep(5)                # Gives the drone time to start
drone.stop() 
time.sleep(.5)

def StopDrone():
	print "Stopping..."
	drone.stop()
	return 1

def DroneHover():
	print "Hovering...."
	drone.hover()

def DroneMove(leftright, backwardforward, downup, turnleftright):
	#movement in x, y, z
	if((leftright == 0) and (backwardforward == 0) and (turnleftright==0)):
		drone.at("PCMD", [0,0.0,0.0,0.0,0.0])
		return 1
	drone.move(leftright, backwardforward, downup, turnleftright)
	# self.at("PCMD", [0,0.0,0.0,0.0,0.0])
	return 1



while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()
	if not ret:
		print "did not get any frames yo"
	else: print "got a frame"

	#storing the height, width, and channel for the frame captured
	h, w, c = frame.shape 
	#process the image, get info about detected object
	processed_image, x_location, center, radius = detectColor(frame, 'yellow')
	middle = w/2.0

	if(radius<15):
		LISTOFVALUES[position_in_array%ARRAYSIZE] = 65
		VALUESFORYAW[position_in_array%ARRAYSIZE] = 320
		position_in_array += 1
	else:
		LISTOFVALUES[position_in_array%ARRAYSIZE] = radius
		VALUESFORYAW[position_in_array%ARRAYSIZE] = x_location
		position_in_array += 1

	error = 0.0
	turn_p = 0.0

	for values in LISTOFVALUES:
		average = average + values

	for values in VALUESFORYAW:
		average_x_location = average_x_location + values

	average = average/ARRAYSIZE

	average_x_location = average_x_location/ARRAYSIZE
	# print average

	left_right = 0;
	forward_backward = 0;
	up_down = 0;
	turn_left_right = 0;

	print average_x_location

	f_error = abs(GOAL_RADIUS-average)
	f_prop = f_error/GOAL_RADIUS
	f_speed = f_prop*F_GAIN

	t_error = abs(middle - average_x_location)
	t_prop = t_error/middle
	t_speed = t_prop * T_GAIN

	if(average_x_location<middle):
		turn_left_right = -t_speed
		print "Move Left"
	elif(average_x_location > middle):
		print "Move Right"
		turn_left_right = t_speed
	else:
		print "ITS IN THE MIDDLE"
		turn_left_right = 0;


	if( 15 <= average < 55):
		forward_backward = f_speed
		print "Move Forwards"
	elif(average > 70):
		forward_backward = -f_speed
		print "Move Backwards"
	else:	
		forward_backward = 0

	DroneMove(left_right, forward_backward, up_down, turn_left_right)
	print average
	
	cv2.startWindowThread()
	cv2.namedWindow("Camera View")
	cv2.imshow('processed_image', processed_image)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

drone.land()                   # Drone lands
time.sleep(3)
