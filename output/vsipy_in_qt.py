from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import pyaudio
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QBrush, QPixmap
import os
from process.video import Thread
from PyQt5.QtGui import QImage, QPixmap

def qt(visualizer_in=None, visualizer_out=None):
    # 把vispy 塞到pyqt
    MainWindow = QMainWindow()  # 主窗体
    MainWindow.resize(553, 715)
    centralwidget = QWidget(MainWindow)
    p = pyaudio.PyAudio()
    # 视频输出下拉

    audio_output_select = QComboBox(centralwidget)
    audio_output_select.setGeometry(QtCore.QRect(10, 290, 451, 21))
    audio_input_select = QComboBox(centralwidget)
    audio_input_select.setGeometry(QtCore.QRect(10, 40, 451, 21))
    # 摄像头
    camera_select = QComboBox(centralwidget)
    camera_select.setGeometry(QtCore.QRect(10, 540, 451, 21))
    camera_label = QLabel(centralwidget)
    camera_label.setGeometry(QtCore.QRect(10, 510, 72, 16))
    audio_output_label = QLabel(centralwidget)
    audio_output_label.setGeometry(QtCore.QRect(10, 260, 451, 31))
    audio_input_label = QLabel(centralwidget)
    audio_input_label.setGeometry(QtCore.QRect(12, 12, 451, 16))
    verticalLayoutWidget = QWidget(centralwidget)
    verticalLayoutWidget.setGeometry(QtCore.QRect(10, 70, 451, 181))
    audio_input_canvas = QVBoxLayout(verticalLayoutWidget)
    audio_input_canvas.setContentsMargins(0, 0, 0, 0)
    verticalLayoutWidget_2 = QWidget(centralwidget)
    verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 320, 451, 171))
    audio_output_canvas = QVBoxLayout(verticalLayoutWidget_2)
    audio_output_canvas.setContentsMargins(0, 0, 0, 0)
    # verticalLayoutWidget_3 = QWidget(centralwidget)
    verticalLayoutWidget_3 = QtWidgets.QLabel(centralwidget)
    verticalLayoutWidget_3.setGeometry(QtCore.QRect(10, 580, 451, 171))

    @pyqtSlot(QImage)
    def setImage(image):
        verticalLayoutWidget_3.setPixmap(QPixmap.fromImage(image))
    th=Thread()
    th.changePixmap.connect(setImage)
    th.start()
    audio_input_canvas.addWidget(visualizer_in.canvas.native)
    audio_output_canvas.addWidget(visualizer_out.canvas.native)
    MainWindow.setCentralWidget(centralwidget)
    _translate = QtCore.QCoreApplication.translate

    # 给下拉框加入选项
    for device in (audio_input_select, audio_output_select, camera_select):
        for item in range(p.get_device_count()):
            item_p = p.get_device_info_by_index(item)
            # print(item_p)
            device.addItem(item_p['name'])

    MainWindow.setWindowTitle(_translate("MainWindow", "AV-MONITOR_by_lucius"))
    camera_label.setText(_translate("MainWindow", "TextLabel"))
    audio_output_label.setText(_translate("MainWindow", "检测到默认音频输出设备: %s" % p.get_default_output_device_info()['name']))
    audio_input_label.setText(_translate("MainWindow", "检测到默认音频输入设备: %s" % p.get_default_input_device_info()['name']))
    QtCore.QMetaObject.connectSlotsByName(MainWindow)
    # MainWindow.show()
    return MainWindow