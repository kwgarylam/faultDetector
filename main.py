from PyQt5 import QtWidgets, QtGui, QtCore
from mainGUI import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog, QApplication, QWidget, QLabel
from PyQt5.QtGui import QImage, QIcon, QPixmap
import cv2, imutils

import sys


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Code to start #
        QtWidgets.QMainWindow.resize(self, 1080, 900)


        # Variables #
        self.filename = None # Hold the image address
        self.originalImg = None # Hold the temporary image
        self.resultImg = None
        self.xbar_now = 49
        self.ybar_now = 49
        self.rbar_now = 49

        # Added Code here #

        # TextBrowser
        self.ui.textBrowser.setText('Hello! Welcome to use this program!')

        # Buttons
        self.ui.pushButton_2.clicked.connect(self.loadImage)

        # Sliders
        self.ui.horizontalSlider.valueChanged['int'].connect(self.set_xValue)
        self.ui.horizontalSlider_2.valueChanged['int'].connect(self.set_yValue)




        ### End of init function ###

    ### Added Code here ###

    def loadImage(self):
        """ This function will load the user selected image
            and set it to label using setPhoto function.
        """
        self.filename = QFileDialog.getOpenFileName(filter="Image (*.*)")[0]
        self.originalImg = cv2.imread(self.filename)
        self.run(self.originalImg)

        #return self.image
        #self.setMainImages(self.image)


    def prepImages(self, myImage, dim):
        """ This function will take image input and resize it. The image will be converted
            to QImage to set at the label.
        """
        #self.originalImg = mainImage
        myImage = cv2.resize(myImage,(dim[0],dim[1]))
        #frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        myImage = QImage(myImage, myImage.shape[1], myImage.shape[0], myImage.strides[0], QImage.Format_BGR888) #Pixmap format
        return myImage


    def updateAllImageLabels(self, mainImage):
        self.ui.label_3.setPixmap(QtGui.QPixmap.fromImage(mainImage))


    ### Sliders for coordinates constraint ###
    def set_xValue(self, value):
        """ This function will set the x position of the constraint """
        self.xbar_now = value
        print ("xbar: ", self.xbar_now)

    def set_yValue(self, value):
        """ This function will set the x position of the constraint """
        self.ybar_now = value
        print ("ybar: ", self.ybar_now)

    #def updateMainImage(self, mainImage, secondImage, resultImage):
    #    self.setImages(self.image)

    def run(self, _mainImage):
        mainImage = self.prepImages(_mainImage, dim=(640, 480))
        self.updateAllImageLabels(mainImage)





    ### Buttons ###










if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
