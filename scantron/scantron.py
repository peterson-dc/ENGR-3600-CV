import argparse
import imutils
import cv2

def detect_rectangle(contour):
	# initialize the shape name and approximate the contour
	peri = cv2.arcLength(contour, True)
	approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
	
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
		return (True, (x, y, w, h))
	else:
		return (False, ())
	
def find_rectangles(contours, img):
	rectangles = []
	# loop through the contours to detect the rectangles
	for contour in new_cnts:
		# determine if the contour is a rectangle
		is_rectangle, rectangle = detect_rectangle(contour)
		# multiply the contour (x, y)-coordinates by the resize ratio,
		# then draw the contours and the name of the shape on the image
		contour = contour.astype("float")
		contour *= ratio
		contour = contour.astype("int")
		if is_rectangle:
			cv2.drawContours(img, [contour], -1, (0, 255, 0), 2)
			rectangles.append(rectangle)

		# show the output image
		if debug:
			cv2.imshow("Cropped Norm Image", resize_image(img, 20))
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	return rectangles


def resize_image(img, percentage):
	width = int(img.shape[1] * percentage / 100)
	height = int(img.shape[0] * percentage / 100)
	dim = (width, height)
	# resize image
	resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
	return resized

def determine_char(img, row_height):
	# character array
	characters = [' ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
	(x, y, w, h) = cv2.boundingRect(img)
	# Find center of mark	
	y = y + (h / 2)
	
	# initial row y coordinate
	row_pos = 0	

	# loop through each row	
	for row in range(0, 27):
		if y > row_pos and y < row_pos + row_height:
			return characters[row]
		row_pos += row_height
	return ''

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to the input image")
ap.add_argument("-d", "--debug", required=False, help="enter debug mode", action="store_true")
args = ap.parse_args()
debug = args.debug

# load the image and resize it to a smaller factor so that
# the shapes can be approximated image
image = cv2.imread(args.image)
#resized = imutils.resize(image, width=300)
ratio = image.shape[0] / float(image.shape[0])
# convert the resized image to grayscale, blur it slightly,
# and threshold it
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY_INV)[1]
#Erode
element = cv2.getStructuringElement(1, (5,5), (-1, 1))
eroded_img = cv2.erode(thresh, element)
#Dilate
dilated_img = cv2.dilate(eroded_img, element)
if debug:
	cv2.namedWindow("Dilated Image", cv2.WINDOW_NORMAL)
	cv2.imshow("Dilated Image", dilated_img)


# Find contours
cnts = cv2.findContours(dilated_img.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

first_rectangle = None

# Find the first bottome right rectangle
for contour in cnts:
	# determine if rectangle
	is_rectangle, first_rectangle = detect_rectangle(contour)
	if is_rectangle:
		# we found the first rectangle
		cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
		break;

if debug:
	print("first rectangle: " + str(first_rectangle))

x, y, w, h = first_rectangle


# crop the image to find lower rectangles
x1 = 0
x2 = x + 60
y1 = y - 30 
y2 = y + h + 30
cropped_image = dilated_img[y1:y2, x1:x2]

cropped_norm_image = image[y1:y2, x1:x2]


# find the contours of the cropped image
new_cnts = cv2.findContours(cropped_image.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
new_cnts = imutils.grab_contours(new_cnts)

# find lower rectangles
lower_rectangles = find_rectangles(new_cnts, cropped_norm_image)

# reverse list to find the first 25 rectangles from the left
lower_rectangles.reverse()

# Crop again to find upper rectangles
x1 = 0
x2 = lower_rectangles[0][0]
y1 = 0
y2 = image.shape[0]

cropped_image = dilated_img[y1:y2, x1:x2]

cropped_norm_image = image[y1:y2, x1:x2]

# find the contours of the cropped image
new_cnts = cv2.findContours(cropped_image.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
new_cnts = imutils.grab_contours(new_cnts)

upper_rectangles = find_rectangles(new_cnts, cropped_norm_image)

# find the difference in y between the bottom two rectangles
# height of rows
height_of_row = upper_rectangles[0][1] - upper_rectangles[1][1]

# Find height of name section
height_of_form = 27 * height_of_row

# Find bottom y coordinate of form
bottom_y = upper_rectangles[0][1] + upper_rectangles[0][3]

# Find top y coordinate of form
top_y = bottom_y - height_of_form

if debug:
	print("Upper Rectangles: " + str(upper_rectangles))
	print("Height of Row: " + str(height_of_row))
	print("Height of Form: " + str(height_of_form))
	print("Bottom y coordinate: " + str(bottom_y))
	print("Top y coordinate: " + str(top_y))

name = ''

# Loop through the form's columns and determine the marked characters
for col in range(1, 26):
	x1 = lower_rectangles[col][0]
	x2 = lower_rectangles[col][0] + lower_rectangles[col][3]
	y1 = top_y
	y2 = bottom_y
	cropped_image = dilated_img[y1:y2, x1:x2]
	cropped_norm_image = image[y1:y2, x1:x2]
	character = determine_char(cropped_image, height_of_row)
	name += character

# print the name
print(name)

if debug:
	while(True):
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

