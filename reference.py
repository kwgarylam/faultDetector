import os
import glob
import cv2
import numpy as np
import time

from PIL import Image, ImageDraw, ImageFilter

from matplotlib import pyplot as plt

######### Get Video - Start ###############
cap = cv2.VideoCapture(2)
######### Get Video - End ###############




################## add circular mask into picture - Start ###############################
thumb_width = 480

def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def mask_circle_solid(centerX, centerY, Radius, pil_img, background_color, blur_radius, offset=0):
    background = Image.new(pil_img.mode, pil_img.size, background_color)

    offset = blur_radius * 2 + offset + 50
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((centerX-Radius-80, centerY-Radius, centerX+Radius-80, centerY+Radius), fill=255)
 #   draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    return Image.composite(pil_img, background, mask)


################## add circular mask into picture - End ###############################



def nothing(x):
    pass

cv2.namedWindow("Tracking")
cv2.createTrackbar("LH", "Tracking", 0, 255, nothing)
cv2.createTrackbar("LS", "Tracking", 91, 255, nothing)
cv2.createTrackbar("LV", "Tracking", 37, 255, nothing)
cv2.createTrackbar("UH", "Tracking", 255, 255, nothing)
cv2.createTrackbar("US", "Tracking", 255, 255, nothing)
cv2.createTrackbar("UV", "Tracking", 255, 255, nothing)

n=0

detect_circle_r = 270

while True:

    check, frame = cap.read()
    cv2.imshow("Capturing", frame)

    if cv2. waitKey(1) == ord('s'):


        cv2.imwrite(filename='temp.jpg', img=frame)

        filename = 'temp.jpg'
        im = Image.open(filename)
        image = cv2.imread(filename)

        ################## Detect Circle - Start ################################################

        output = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # detect circles in the image
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 200, 30, 100, 100, 110)

        if(circles is None):
            continue

    #    print(circles[0,0,0])
    #    print(circles[0,0,1])
    #    print(circles[0,0,2])

        detect_cricle_x = circles[0,0,0]
        detect_circle_y = circles[0,0,1]
        detect_circle_r = circles[0,0,2]



        print(detect_cricle_x)
        print(detect_circle_y)
        print("R")
        print(detect_circle_r)

        # ensure at least some circles were found
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")

            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            # show the output image
        cv2.imshow("output", np.hstack([image, output]))
        #	cv2.waitKey(0)

        ################## Detect Circle - End ################################################

        mask_radius = 170

        ################## Mask the captured picture - Start ##################################
        im_square = crop_max_square(im).resize((thumb_width, thumb_width), Image.LANCZOS)
        im_thumb = mask_circle_solid(detect_cricle_x, detect_circle_y, mask_radius, im_square, (0, 0, 0), 0)

        im_thumb.save('Mask-pic.jpg', quality=95)

        ################## Mask the captured picture - End ##################################

        img = cv2.imread('Mask-pic.jpg')
        frame = cv2.imread('Mask-pic.jpg')

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        l_h = cv2.getTrackbarPos("LH", "Tracking")
        l_s = cv2.getTrackbarPos("LS", "Tracking")
        l_v = cv2.getTrackbarPos("LV", "Tracking")

        u_h = cv2.getTrackbarPos("UH", "Tracking")
        u_s = cv2.getTrackbarPos("US", "Tracking")
        u_v = cv2.getTrackbarPos("UV", "Tracking")

        l_b = np.array([l_h, l_s, l_v])
        u_b = np.array([u_h, u_s, u_v])

        mask = cv2.inRange(hsv, l_b, u_b)

        res = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)
        cv2.imshow("res", res)


        cv2.imshow("img",img)

        plt.hist(mask.ravel(), 256, [0,256])
      #  plt.show()

    ##################### Find the pixel value - Start #####################

     #   pixelWhite = np.bincount(img.ravel(), minlength=256)
        pixelcount = cv2.calcHist([mask], [0], None, [256], [0, 256])

      #  print(pixelcount [0])
      #  print(pixelcount [255])

        pixelwhite = int(pixelcount[255])
        pixelblack = int(pixelcount[0])

        pixelresult = (pixelblack/(pixelblack+pixelwhite)*100)
        print(pixelwhite)
        print(pixelblack)
        print(pixelresult)

    ##################### Find the pixel value - End #####################

        if pixelresult > 99.7:
            Result_message = str(round(pixelresult,2))+ "%" + "\n" + "PASS"
        else:
            Result_message = str(round(pixelresult,2))+ '%' + "\n"  + "FAIL"

        cv2.putText(
            image,  # numpy array on which text is written
            Result_message,  # text
            (10,50),  # position at which writing has to start
            cv2.FONT_HERSHEY_SIMPLEX,  # font family
            1,  # font size
            (209, 255, 0, 255),  # font color
            3)  # font stroke

      #  draw.text(image,(0,0),"TESTING",)
        cv2.imshow("Result",image)


        key = cv2.waitKey(1)
        if key == 27:
            break

cv2.destroyAllWindows()

cv2.waitKey(0)


