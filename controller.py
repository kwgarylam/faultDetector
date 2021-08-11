from PyQt5 import QtWidgets, QtGui
from view import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage
from PyQt5.Qt import QThreadPool,QRunnable, pyqtSlot
from imutils.video import WebcamVideoStream
import model
import cv2
import numpy as np
import datetime

import sys

runable = False
#originalImg = None

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Code to start #
        QtWidgets.QMainWindow.resize(self, 1170, 880)


        # Variables #
        self.filename = None # Hold the image address
        self.originalImg = np.zeros((640,480,3), dtype=np.uint8) # Hold the temporary image
        self.middleImg = np.zeros((320,240,3), dtype=np.uint8)
        self.resultImg = np.zeros((320,240,3), dtype=np.uint8)
        self.videoFlag = False
        self.xbar_now = 320
        self.ybar_now = 240
        self.rbar_now = 120
        self.thesh_min_bar_now = 144
        self.thesh_max_bar_now = 336
        self.totalPixels = 0
        self.sumOfArea = 0
        self.defect = 0
        self.dim = [640,480]
        #global originalImg


        # Added Code here #

        # TextBrowser
        self.ui.textBrowser.setText('Hello! Welcome to use this program!')

        # Buttons
        self.ui.pushButton.clicked.connect(self.savePhotos)
        self.ui.pushButton_2.clicked.connect(self.loadImage)
        self.ui.pushButton_3.clicked.connect(self.startChecking)
        self.ui.pushButton_4.clicked.connect(self.stopChecking)

        # Radio Buttons
        self.ui.radioButton.clicked.connect(self.photoIsClicked)
        self.ui.radioButton_2.clicked.connect(self.cameraIsClicked)

        # Sliders
        self.ui.horizontalSlider.valueChanged['int'].connect(self.set_xValue)
        self.ui.horizontalSlider_2.valueChanged['int'].connect(self.set_yValue)
        self.ui.horizontalSlider_3.valueChanged['int'].connect(self.set_rValue)
        self.ui.verticalSlider.valueChanged['int'].connect(self.set_thesh_min)
        self.ui.verticalSlider_2.valueChanged['int'].connect(self.set_thesh_max)



        ### End of init function ###

    ### Added Code here ###
    def runModel(self):
        self.middleImg, self.resultImg, self.totalPixels, self.sumOfArea, self.defect, = model.run(self.originalImg,
                                                                                                   self.rbar_now,
                                                                                                   self.xbar_now,
                                                                                                   self.ybar_now,
                                                                                                   self.thesh_min_bar_now,
                                                                                                   self.thesh_max_bar_now)

    def photoIsClicked(self):
        self.ui.pushButton_2.setEnabled(True)

    def cameraIsClicked(self):
        self.ui.pushButton_2.setEnabled(False)

    def debugLog(self, myString):
        self.ui.textBrowser.setText(myString)
        print(myString)

    def startChecking(self):
        global runable
        #global originalImg
        runable = True
        print("Start detection!")
        try:
            if self.ui.radioButton.isChecked():
                self.ui.statusbar.showMessage("Image mode is used.")
                print("Image mode is used.")
                self.ui.radioButton.setEnabled(False)
                self.ui.radioButton_2.setEnabled(False)
                ### Detection Started ###
                self.runModel()
                self.updateDetection()

            elif self.ui.radioButton_2.isChecked():
                self.ui.statusbar.showMessage("Video mode is used.")
                print("Video mode is used.")
                self.ui.radioButton.setEnabled(False)
                self.ui.radioButton_2.setEnabled(False)

                ### Detection Started ###
                vs = WebcamVideoStream(src=0).start()

                while runable:

                    try:
                        self.originalImg = vs.read()
                        self.runModel()
                        self.updateDetection()

                    except:
                        print("Exception in graping video")
                        pass


            else:
                self.ui.statusbar.showMessage("Error is choosing detection mode.")
                print("Error in mode")
        except:
            self.debugLog("Error in reading file ...")

    def stopChecking(self):
        global runable
        runable = False
        self.ui.radioButton.setEnabled(True)
        self.ui.radioButton_2.setEnabled(True)
        self.ui.statusbar.showMessage("Stop detection.")
        print("Stop detection")

    def loadImage(self):
        """ This function will load the user selected image
            and set it to label using setPhoto function.
        """
        if self.ui.radioButton.isChecked():
            #self.ui.pushButton_2.setEnabled(True)
            self.filename = QFileDialog.getOpenFileName(filter="Image (*.*)")[0]
            #global originalImg
            self.originalImg = cv2.imread(self.filename)
            self.ui.label_3.setText('Image loaded \nPlease press "Start" button for detection.')
            self.debugLog('Image loaded ... ')
        else:
            pass


    def formatImages(self, myImage, dim):
        """ This function will take image input and resize it. The image will be converted to QImage.
        """
        myImage = cv2.resize(myImage,(dim[0],dim[1]))
        myImage = QImage(myImage, myImage.shape[1], myImage.shape[0], myImage.strides[0], QImage.Format_BGR888) #Pixmap format
        return myImage


    ### Sliders for coordinates constraint ###
    def set_xValue(self, value):
        """ This function will set the x position of the constraint """
        self.xbar_now = value + 1
        self.xbar_now = round(self.xbar_now / 100, 1)
        self.xbar_now = round(self.dim[0] * self.xbar_now, 1)
        print ("xbar: ", self.xbar_now)

    def set_yValue(self, value):
        """ This function will set the y position of the constraint """
        self.ybar_now = value + 1
        self.ybar_now = self.ybar_now / 100
        self.ybar_now = round(self.dim[1] * self.ybar_now, 1)
        print ("ybar: ", self.ybar_now)

    def set_rValue(self, value):
        """ This function will set the r position of the constraint """
        self.rbar_now = value + 1
        self.rbar_now = self.rbar_now / 100
        self.rbar_now = round((self.dim[1] // 2) * self.rbar_now)
        print ("rbar: ", self.rbar_now)

    def set_thesh_min(self, value):
        """ This function will set the r position of the constraint """
        self.thesh_min_bar_now = value + 1
        self.thesh_min_bar_now = self.thesh_min_bar_now / 100
        self.thesh_min_bar_now = int(round(self.thesh_min_bar_now * self.dim[1], 1))
        print ("min bar: ", self.thesh_min_bar_now)

    def set_thesh_max(self, value):
        """ This function will set the r position of the constraint """
        self.thesh_max_bar_now = value + 1
        self.thesh_max_bar_now = self.thesh_max_bar_now / 100
        self.thesh_max_bar_now = int(round(self.thesh_max_bar_now * self.dim[1], 1))
        print ("max bar: ", self.thesh_max_bar_now)

    ### Updates ###
    def updateAllImageLabels(self, _mainImage, _middleImage, _resultImage):
        self.ui.label_3.setPixmap(QtGui.QPixmap.fromImage(_mainImage))
        self.ui.label_4.setPixmap(QtGui.QPixmap.fromImage(_middleImage))
        self.ui.label_5.setPixmap(QtGui.QPixmap.fromImage(_resultImage))

    def updateImageLabels(self, _mainImage, _middleImage):
        self.ui.label_3.setPixmap(QtGui.QPixmap.fromImage(_mainImage))
        self.ui.label_4.setPixmap(QtGui.QPixmap.fromImage(_middleImage))


    def updateDetection(self):
        formatedMainImage = self.formatImages(self.originalImg, dim=(640, 480))
        formatedMiddleImage = self.formatImages(self.middleImg, dim=(320, 240))

        ############################################
        if self.resultImg > 0:
            formatedResultImg = self.formatImages(self.resultImg, dim=(320, 240))
            self.updateAllImageLabels(formatedMainImage, formatedMiddleImage, formatedResultImg)
        else:
            self.updateImageLabels(formatedMainImage, formatedMiddleImage)

        ##################################################
        
        self.checkResult()
        cv2.waitKey(1)


    def checkResult(self):
        if self.defect >= 0.4:
            self.ui.label_10.setText('Fail!')
            self.ui.label_10.setStyleSheet("background-color: red; font: 75 12pt;")
            print("Fail!")
            self.debugLog("Total pixel: " + str(self.totalPixels) + "\n" +
                          "Sum of Area: " + str(self.sumOfArea) + "\n" +
                          "Defect : " + str(self.defect) + "%" + "\n" +
                          "Fail!")

        elif self.defect < 0.4 and self.defect > 0:
            self.ui.label_10.setText('Pass')
            self.ui.label_10.setStyleSheet("background-color: rgb(85, 255, 0); font: 75 12pt;")
            self.debugLog("Total pixel: " + str(self.totalPixels) + "\n" +
                          "Sum of Area: " + str(self.sumOfArea) + "\n" +
                          "Defect : " + str(self.defect) + "%" + "\n" +
                          "Pass!")
            print("Pass")
        else:
            self.ui.label_10.setText('Detecting')
            self.ui.label_10.setStyleSheet("background-color: orange; font: 75 12pt;")

    def savePhotos(self):
        try:
            #global originalImg
            im_h = cv2.hconcat([self.originalImg, self.resultImg])
            timestamp = datetime.datetime.today().strftime("%Y-%m-%d_%H%M")
            filename = "output/result" + "_" + timestamp + ".jpg"
            cv2.imwrite(filename, im_h)
            self.ui.statusbar.showMessage("File saved in /" + filename)
            print("Image saved! ", filename)
        except:
            print("Error in saving photos")
            self.ui.statusbar.showMessage("Error in saving photos")



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    print("Program Closed...")
