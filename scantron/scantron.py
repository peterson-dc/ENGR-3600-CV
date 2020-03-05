import argparse
import imutils
import cv2

def detect_rectangle(c, rectangles):
	# initialize the shape name and approximate the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.04 * peri, True)
	
	# if the shape has 4 vertices, it is either a square or
	# a rectangle
	if len(approx) == 4:
		# compute the bounding box of the contour and use the
		# bounding box to compute the aspect ratio
		(x, y, w, h) = cv2.boundingRect(approx)
		ar = w / float(h)
		# a square will have an aspect ratio that is approximately
		# equal to one, otherwise, the shape is a rectangle
		shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
		print(shape)
		print((x, y, w, h))
		rectangles.append(c)
		return True
	else:
		return False
	
def resize_image(img, percentage):
	width = int(img.shape[1] * percentage / 100)
	height = int(img.shape[0] * percentage / 100)
	dim = (width, height)
	# resize image
	resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
	return resized

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
args = vars(ap.parse_args())

# load the image and resize it to a smaller factor so that
# the shapes can be approximated image
image = cv2.imread(args["image"])
#resized = imutils.resize(image, width=300)
ratio = image.shape[0] / float(image.shape[0])
# convert the resized image to grayscale, blur it slightly,
# and threshold it
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow("Gray", resize_image(gray, 20))
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY_INV)[1]
cv2.imshow("Threshold", resize_image(thresh, 20))
#Erode
element = cv2.getStructuringElement(1, (5,5), (-1, 1))
eroded_img = cv2.erode(thresh, element)
#Dilate
dilated_img = cv2.dilate(eroded_img, element)
cv2.imshow("Dilated", resize_image(dilated_img, 20))


# find contours in the thresholded image and initialize the
# shape detector
cnts = cv2.findContours(dilated_img.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
rectangles = []


# loop over the contours
for c in cnts:
	# compute the center of the contour, then detect the name of the
	# shape using only the contour
	#M = cv2.moments(c)
	#cX = int((M["m10"] / M["m00"]) * ratio)
	#cY = int((M["m01"] / M["m00"]) * ratio)
	is_rectangle = detect_rectangle(c, rectangles)
	# multiply the contour (x, y)-coordinates by the resize ratio,
	# then draw the contours and the name of the shape on the image
	c = c.astype("float")
	c *= ratio
	c = c.astype("int")
	if is_rectangle:
		cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
	#cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
	#	0.5, (255, 255, 255), 2)

	# show the output image
	cv2.imshow("Image", resize_image(image, 20))
	if cv2.waitKey(1) & 0xFF == ord('q'):
        	break

