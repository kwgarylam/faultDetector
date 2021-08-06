import cv2
import numpy as np
import myUtlis as utlis

# Variables
height = 640
width = 480
dim = (height, width)

middleImg = None
resultImg = None


def run(img, ROI, _x_value, _y_value, _min_value, _max_value):

    totalPixels, sumOfArea, defect = 0, 0, 0

    # Resize the image to default size
    if (img.shape[:2]) != (height, width):
        img = cv2.resize(img, (640, 480))
        output = img.copy()


    ######################################################
    # Function to pick the range of the HSV image
    # lower, upper = utlis.colorPicker(originalImg)
    ######################################################

    ################################ Prepare the ROI for detection ################################
    ###############################################################################################
    # Detecting the outline of the big circle
    # Filter out the unwanted color range and return the interested pixels
    lower = np.array([0, 0, 0])
    upper = np.array([179, 100, 230])
    colorMasked = utlis.colorMasker(img, lower, upper, display=False)

    # Image Preprocessing
    gray = cv2.cvtColor(colorMasked, cv2.COLOR_BGR2GRAY)
    midianBlur = cv2.medianBlur(gray, 5)

    # Find the Region of Interest (ROI)
    ROI = round(ROI/100,1)
    secondROI = ROI - 0.2
    if secondROI <= 0.2:
        secondROI = 0.2

    x_value = round(_x_value / 100, 1)
    y_value = round(_y_value / 100, 1)

    min_value = round(_min_value / 100, 1)
    max_value = round(_max_value / 100, 1)

    #print(min_value)
    #print(max_value)


    ### Cropping the ROI ###
    ret, thresh = cv2.threshold(midianBlur, 127, 255, cv2.THRESH_BINARY)
    x, y, r = utlis.getCircle(thresh, img, _h=y_value, _w=x_value, display=True, ROIpercent=ROI, _radius_threshold=(min_value, max_value))
    firstMasked = utlis.cropROI(output, (x, y, r), display=False)

    # Second Filter
    colorMasked2 = utlis.colorMasker(firstMasked, lower, upper, display=False)
    gray2 = cv2.cvtColor(colorMasked2, cv2.COLOR_BGR2GRAY)
    midianBlur2 = cv2.medianBlur(gray2, 5)
    ret, thresh2 = cv2.threshold(midianBlur2, 127, 255, cv2.THRESH_BINARY)
    try:
        x2, y2, r2 = utlis.getCircle(thresh2, img, display=False, ROIpercent=secondROI, _radius_threshold=(0.1, 0.3), dp=8, minDist=300)
        secondMasked = utlis.cropROI(output, (x, y, r), (x2, y2, r2), display=False)

        ### END of ROI Filter ###

        ### Filter Algorithm ###
        graySecondMasked = cv2.cvtColor(secondMasked, cv2.COLOR_BGR2GRAY)
        midianBlurSecondMasked = cv2.medianBlur(graySecondMasked, 5)
        totalPixels = cv2.countNonZero(midianBlurSecondMasked)

        edges = cv2.Canny(midianBlurSecondMasked, 100, 200)
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        sumOfArea = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # print(area)
            if area <= 150 and area > 0:
                # pass
                cv2.drawContours(output, cnt, -1, (200, 0, 150), 3)
                sumOfArea = sumOfArea + area

        #print("Number of total pixel: ", totalPixels)
        #print("SumOfArea = ", sumOfArea)

        defect = round((sumOfArea / totalPixels) * 100.0, 3)
        #print("Defect = ", defect, "%")

        ## For Debug
        middleImg = img
        resultImg = output

    except:
        print("Error Caught in second filter")
        middleImg = img
        resultImg = 0
        defect = -1

    #print (totalPixels, sumOfArea, defect)

    return middleImg, resultImg, totalPixels, sumOfArea, defect
