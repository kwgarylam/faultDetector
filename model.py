import cv2
import numpy as np
import myUtlis as utlis

def run(img, ROI, x_value, y_value, min_value, max_value):
    # Variables
    height = 640
    width = 480
    dim = (height, width)
    r2 = 130
    copyResultFlag = 0

    middleImg = np.zeros((320, 240, 3), dtype=np.uint8)

    resultImg = np.zeros((320, 240, 3), dtype=np.uint8)


    totalPixels, sumOfArea, defect = 0, 0, 0

    # Resize the image to default size
    if (img.shape[:2]) != (height, width):
        img = cv2.resize(img, (640, 480))
        output = img.copy()

    try:
        lower = np.array([0, 0, 0])
        upper = np.array([179, 100, 230])
        colorMasked = utlis.colorMasker(img, lower, upper, display=False)
        # Image Preprocessing
        gray = cv2.cvtColor(colorMasked, cv2.COLOR_BGR2GRAY)
        midianBlur = cv2.medianBlur(gray, 5)

        ret, thresh = cv2.threshold(midianBlur, 127, 255, cv2.THRESH_BINARY)

        x, y, r = utlis.getCircle(thresh, img, _h=y_value, _w=x_value, display=True, ROI_radius=ROI, _radius_threshold=(min_value, max_value))

        maskedLayer = utlis.cropROI(output, (x, y, r), (x, y, r2), display=False)

        ####
        grayMasked = cv2.cvtColor(maskedLayer, cv2.COLOR_BGR2GRAY)
        midianBlurMasked = cv2.medianBlur(grayMasked, 5)
        totalPixels = cv2.countNonZero(midianBlurMasked)

        edges = cv2.Canny(midianBlurMasked, 100, 200)
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            # print(area)
            if area <= 150 and area > 0:
                # pass
                cv2.drawContours(output, cnt, -1, (200, 0, 150), 3)
                sumOfArea = sumOfArea + area

        defect = round((sumOfArea / totalPixels) * 100.0, 3)
        middleImg = img
        resultImg = output
        oldResult = resultImg



    except:
        print("No object detected in the model")
        middleImg = img
        resultImg = oldResult
        #resultImg = 0
        defect = -1


    return middleImg, resultImg, totalPixels, sumOfArea, defect
