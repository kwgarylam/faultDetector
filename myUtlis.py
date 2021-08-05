import cv2
import numpy as np

# Method to translate OpenCV coordinate to Geometry Coordinate
# i.e. the (0,0) is set to the center of the image
def cv2Geo(point, center_offset):
    point[0] = point[0] - center_offset[0]
    point[1] = -point[1] - center_offset[1]
    return point

# Method to translate Geometry Coordinate to OpenCV coordinate
# i.e. the (0,0) is set to the top-left conner of the image
def geo2Cv(point, center_offset):
    point[0] = point[0] + center_offset[0]
    point[1] = -point[1] + center_offset[1]
    return point

# Method to get the center of the lens circle
# Return the circle that inside the Region of Interest (ROI)
# i.e. The %of the image from the center
def getCircle(grayImg, outputImg, _h, _w, display=True, ROIpercent=0.5, radius_threshold=(210, 230), dp=1.2, minDist=100):

    # Get the height and width of the image
    h, w = grayImg.shape

    _x, _y, _r = 0, 0, 0

    center = [w//2, h//2]

    #geo_center = geo2Cv([-100,0],center)
    #print(geo_center)
    #cv2.circle(outputImg, (geo_center[0], geo_center[1]), 10, (255, 0, 0), 3)

    ROI_radius = round(center[0]*ROIpercent)
    #circle_radius = []

    if display:
        cv2.circle(outputImg, (center[0], center[1]), ROI_radius, (255, 0, 0), 3)

    # detect circles in the image
    circles = cv2.HoughCircles(grayImg, cv2.HOUGH_GRADIENT, dp, minDist)
    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over the (x, y) coordinates and radius of the circles

        for (x, y, r) in circles:
            # Check whether the circle center is inside the ROI
            if ((abs(x - center[0]) < ROI_radius) and (abs(y - center[1]) < ROI_radius)):
                if (r > radius_threshold[0]) and (r < radius_threshold[1]):

                    text = str(x) + ", " + str(y)
                    cv2.putText(outputImg, text, (x, y+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 1, cv2.LINE_AA)

                    # draw the circle in the output image, then draw a rectangle
                    # corresponding to the center of the circle
                    cv2.circle(outputImg, (x, y), r, (0, 255, 0), 4)
                    cv2.rectangle(outputImg, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                    _x, _y, _r = x, y, r

        # show the output image
        if display:
            cv2.imshow("ROI", outputImg)

            #cv2.waitKey(0)

        return _x, _y, _r


def simpleCircleDetection(img, outputImg):
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # detect circles in the image
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 6, 300)
    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(outputImg, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(outputImg, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    return outputImg

# Function to crop the ROI by mask
def cropROI(img, outerCircle, innerCircle = [0,0,0], dim = (480, 640), display=True):
    mask = np.zeros(dim, dtype="uint8")
    cv2.circle(mask, (outerCircle[0],outerCircle[1]), outerCircle[2], 255, -1)
    cv2.circle(mask, (innerCircle[0], innerCircle[1]), innerCircle[2], 0, -1)

    masked = cv2.bitwise_and(img, img, mask= mask)
    if display:
        cv2.imshow("Masked ROI", masked)

    return masked

def empty(a):
    pass

def colorPicker(img):
    # Track Bar to calibrate the parameters
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.namedWindow("HSV")
    cv2.resizeWindow("HSV", 640, 320)
    cv2.createTrackbar("Hue Min", "HSV", 0, 179, empty)
    cv2.createTrackbar("Hue Max", "HSV", 179, 179, empty)
    cv2.createTrackbar("Sat Min", "HSV", 0, 255, empty)
    cv2.createTrackbar("Sat Max", "HSV", 255, 255, empty)
    cv2.createTrackbar("Value Min", "HSV", 0, 255, empty)
    cv2.createTrackbar("Value Max", "HSV", 255, 255, empty)

    while True:
        # Get the values from
        h_min = cv2.getTrackbarPos("Hue Min", "HSV")
        h_max = cv2.getTrackbarPos("Hue Max", "HSV")
        s_min = cv2.getTrackbarPos("Sat Min", "HSV")
        s_max = cv2.getTrackbarPos("Sat Max", "HSV")
        v_min = cv2.getTrackbarPos("Value Min", "HSV")
        v_max = cv2.getTrackbarPos("Value Max", "HSV")

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(imgHSV, lower, upper)

        result = cv2.bitwise_and(img, img, mask=mask)

        cv2.imshow('Color Picker', result)

        if cv2.waitKey(10) & 0xFF == ord('s'):
            break

    print (lower, upper)
    return lower, upper

def colorMasker(img, lower, upper, display=True):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(imgHSV, lower, upper)
    masked = cv2.bitwise_and(img, img, mask=mask)
    if display:
        cv2.imshow("Masked image", masked)

    return masked
