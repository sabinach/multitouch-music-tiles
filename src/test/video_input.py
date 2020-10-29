import cv2

camera_port = 0
camera = cv2.VideoCapture(camera_port)

while True:
	ret, frame = camera.read()
	cv2.imshow('window',frame)
	cv2.waitKey(100)