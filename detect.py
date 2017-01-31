# Benjamin Ramirez, Alexander Barrick
# returning coordinates of the largest contour, given a color to detect
# inspired by ball tracking at http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
import time, sys
import cv2                                         
import numpy as np


color_dict = {'green' : ((29, 86, 6),(64, 255, 255)),
	'red_orange': ((0, 20, 100),(5, 255, 255)),
	'red': ((160, 50, 50),(180, 255,255)),
	'orange': ((5,50,5),(15,255,255)),
	'blue': ((115, 10, 10),(130, 150, 150)),
	'purple': ((138, 0, 0),(145, 150, 150)),
	'light_blue': ((90, 100, 100),(100, 255, 255)),
	'yellow': ((18, 120,120), (30, 255,255))}

	# 'yellow': ((22, 70,50), (30, 255,255))


def detectColor(image, color):
	ranges = color_dict[color]
	low_color = ranges[0]
	high_color = ranges[1]
	# converting form BGR to HSV
	#getting rid of things not in the desired color range
	imhsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	thresh = cv2.inRange(imhsv, low_color, high_color)
	thresh =cv2.erode(thresh, None, iterations = 2)
	thresh = cv2.dilate(thresh,None, iterations = 2)

	contours = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
	radius = 0
	x = 0
	y = 0
	# to draw the contours, check if there were any within the range specified, get the largest
	# and enclose it with a circle
	if(len(contours) > 0):
		largest = max(contours, key= cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(largest)
		M = cv2.moments(largest)
		x_location = int(x)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		#now we draw it
		cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 0), 2)
		cv2.circle(image, center, 3, (0,255,255), -1) #the center dot
		# print "Center: ", center, "x_coord: ", x, "Radius: ", radius
	else: print "No contours found"

	return image, x, center, radius


#face detection: we take an image and draw a rectangle around all faces found
def detectFace(image):

	face_cascade = cv2.CascadeClassifier('./cascades/haarcascade_frontalface_default.xml')
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# detect the faces in the image
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)

	for (x,y,w,h) in faces:
		cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)

	return image
