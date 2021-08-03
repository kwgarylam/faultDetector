import cv2
import numpy as np
import myUtlis as utlis

height = 480
width = 640

dim = (height, width)

def main():
    # Read the original image from path
    img = cv2.imread('images/1.jpg')

    # Resize the image to default size
    if (img.shape[:2]) != (height, width):
        img = cv2.resize(img, dim)

    # Copy a image for output result
    originalImg = img.copy()

    ######################################################
    # Function to pick the range of the HSV image
    # lower, upper = utlis.colorPicker(originalImg)
    ######################################################

    #########################################################
    # Detecting the outline of the big circle
    # Filter out the unwanted color range and return the interested pixels
    lower = np.array([0, 0, 0])
    upper = np.array([179, 100, 230])
    colorMasked = utlis.colorMasker(img, lower, upper)

    # Image Preprocessing
    gray = cv2.cvtColor(colorMasked, cv2.COLOR_BGR2GRAY)
    midianBlur = cv2.medianBlur(gray,5)

    # Find the Region of Interest (ROI)
    ret, thresh = cv2.threshold(midianBlur, 127, 255, cv2.THRESH_BINARY)
    x, y, r = utlis.getCircle(thresh, img, display=True, ROIpercent=0.3, radius_threshold=(150,300))

    firstMasked = utlis.cropROI(originalImg, (x, y, r), display=True)

    #cv2.imshow('firstMasked', firstMasked)

    ######################################################
    # Detect the outline of the inner circle
    #lower = np.array([0, 0, 150])
    #upper = np.array([60, 100, 255])
    colorMasked2 = utlis.colorMasker(firstMasked, lower, upper)
    gray2 = cv2.cvtColor(colorMasked2, cv2.COLOR_BGR2GRAY)
    midianBlur2 = cv2.medianBlur(gray2, 5)
    ret, thresh2 = cv2.threshold(midianBlur2, 127, 255, cv2.THRESH_BINARY)
    #secondMasked = utlis.simpleCircleDetection(thresh2, originalImg)
    x2, y2, r2 = utlis.getCircle(thresh2, img, display=True, ROIpercent=0.3, radius_threshold=(50,150), dp=8, minDist=300)
    print(x2, y2, r2)
    secondMasked = utlis.cropROI(originalImg, (x, y, r), (x2, y2, r2), display=True)



    ##

    #gray2 = cv2.cvtColor(firstMasked, cv2.COLOR_BGR2GRAY)
    #midianBlur2 = cv2.medianBlur(gray2, 5)
    #ret, thresh2 = cv2.threshold(midianBlur2, 127, 255, cv2.THRESH_BINARY)


    #x, y, r = utlis.getCircle(thresh2, firstMasked, display=True, ROIpercent=0.3, radius_threshold=(150, 300))
    #secondMasked = utlis.cropROI(originalImg, (x, y, r), display=True)





    edges = cv2.Canny(gray,100,200)




    #cv2.imshow('Original Image', originalImg)
    #cv2.imshow('Edges', edges)
    #cv2.imshow('Thresh', thresh)



if __name__ == '__main__':
    main()

cv2.waitKey(0)
cv2.destroyAllWindows()
print("Problem Finished... ")
