from PyQt5 import QtWidgets, QtGui
from view import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage
from PyQt5.Qt import QThreadPool,QRunnable, pyqtSlot
import model
import cv2
import datetime

import sys

runable = False

class myWorker(QRunnable):
    @pyqtSlot()
    def run(self):
        ''' Your code of thread goes in this function
        '''
        global runable
        print("Thread start")

        while(runable):
            try:
                print("In the thread")
            except:
                print("An exception in thread occurred!")
        print("Thread program stopped!")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.threadpool = QThreadPool()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Code to start #
        QtWidgets.QMainWindow.resize(self, 1170, 880)


        # Variables #
        self.filename = None # Hold the image address
        self.originalImg = None # Hold the temporary image
        self.middleImg = None
        self.resultImg = None
        self.videoFlag = False
        self.xbar_now = 49
        self.ybar_now = 49
        self.rbar_now = 49
        self.thesh_min_bar_now = 29
        self.thesh_max_bar_now = 69
        self.totalPixels = 0
        self.sumOfArea = 0
        self.defect = 0


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
    def photoIsClicked(self):
        self.ui.pushButton_2.setEnabled(True)

    def cameraIsClicked(self):
        self.ui.pushButton_2.setEnabled(False)

    def debugLog(self, myString):
        self.ui.textBrowser.setText(myString)
        print(myString)

    def startChecking(self):
        global runable
        runable = True
        try:
            if self.ui.radioButton.isChecked():
                self.ui.statusbar.showMessage("Image mode is used.")
                print("Image mode is used.")
                self.ui.radioButton.setEnabled(False)
                self.ui.radioButton_2.setEnabled(False)
                ### Detection Started ###
                self.runDetection()

            elif self.ui.radioButton_2.isChecked():
                self.ui.statusbar.showMessage("Video mode is used.")
                print("Video mode is used.")
                self.ui.radioButton.setEnabled(False)
                self.ui.radioButton_2.setEnabled(False)
                ### Detection Started ###
                if runable:
                    # Start the thread
                    worker = myWorker()
                    self.threadpool.start(worker)


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
        #print ("xbar: ", self.xbar_now)

    def set_yValue(self, value):
        """ This function will set the y position of the constraint """
        self.ybar_now = value + 1
        #print ("ybar: ", self.ybar_now)

    def set_rValue(self, value):
        """ This function will set the r position of the constraint """
        self.rbar_now = value + 1
        #print ("rbar: ", self.rbar_now)

    def set_thesh_min(self, value):
        """ This function will set the r position of the constraint """
        self.thesh_min_bar_now = value + 1
        print ("min bar: ", self.thesh_min_bar_now)

    def set_thesh_max(self, value):
        """ This function will set the r position of the constraint """
        self.thesh_max_bar_now = value + 1
        print ("max bar: ", self.thesh_max_bar_now)

    ### Updates ###
    def updateAllImageLabels(self, _mainImage, _middleImage, _resultImage):
        self.ui.label_3.setPixmap(QtGui.QPixmap.fromImage(_mainImage))
        self.ui.label_4.setPixmap(QtGui.QPixmap.fromImage(_middleImage))
        self.ui.label_5.setPixmap(QtGui.QPixmap.fromImage(_resultImage))


    def runDetection(self):
        tempImg = self.originalImg.copy()

        self.middleImg, self.resultImg, self.totalPixels, self.sumOfArea, self.defect, = model.run(tempImg,
                                                                                                   self.rbar_now,
                                                                                                   self.xbar_now,
                                                                                                   self.ybar_now,
                                                                                                   self.thesh_min_bar_now,
                                                                                                   self.thesh_max_bar_now)

        formatedMainImage = self.formatImages(self.originalImg, dim=(640, 480))
        formatedMiddleImage = self.formatImages(self.middleImg, dim=(320, 240))
        formatedResultImg = self.formatImages(self.resultImg, dim=(320, 240))

        self.updateAllImageLabels(formatedMainImage, formatedMiddleImage, formatedResultImg)

        self.debugLog("Total pixel: " + str(self.totalPixels) + "\n" +
                      "Sum of Area: " + str(self.sumOfArea) + "\n" +
                      "Defect : " + str(self.defect) + "%")

        self.checkResult()


    def checkResult(self):
        if self.defect >= 0.5:
            self.ui.label_10.setText('Fail!')
            self.ui.label_10.setStyleSheet("background-color: red; font: 75 12pt;")
            print("Fail!")
        elif self.defect < 0.5 and self.defect >= 0:
            self.ui.label_10.setText('Pass')
            self.ui.label_10.setStyleSheet("background-color: rgb(85, 255, 0); font: 75 12pt;")
            print("Pass")
        else:
            self.ui.label_10.setText('Detecting')
            self.ui.label_10.setStyleSheet("background-color: orange; font: 75 12pt;")

    def savePhotos(self):
        try:
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
