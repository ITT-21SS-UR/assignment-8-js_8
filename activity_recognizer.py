import pyqtgraph as pg
import numpy as np
import sys
import pyqtgraph.flowchart.library as fclib

from enum import Enum
from PyQt5 import uic
from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Qt import QtWidgets
from sklearn import svm
from sklearn.exceptions import NotFittedError
from scipy import signal

from DIPPID import SensorUDP, SensorSerial, SensorWiimote
from DIPPID_pyqtnode import BufferNode, DIPPIDNode



class ModusNode(Enum): 
    TRAINING = 1
    PREDICTION = 2
    INACTIVE = 3
    
class GestureNode(Node, QtWidgets.QWidget):
    nodeName = "ActivityRecognition"
    saved_gestures = {}

    def __init__(self, name):
        self.__state = ModusNode.INACTIVE
        self.__is_recording = False
        self.classifier = svm.SVC(kernel='linear') # TODO correct one?

        # TODO init ui for add new gesture
        # TODO init ui for start recording
        # TODO init ui for managing gestures (e.g. delete, retrain)
        self.setup_ui()

        terminals = {
            'in': dict(io='in'), # TODO
            'out': dict(io='out')
        }
        Node.__init__(self, name, terminals=terminals)

    def setup_ui(self):
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        #self.layout = QtWidgets.QVBoxLayout

        # Add new node
        label = QtGui.QLabel("Gesture Name:")
        self.layout.addWidget(label)
        self.text = QtGui.QLineEdit()
        self.action = "Walking"
        self.text.setText(self.action)
        self.layout.addWidget(self.text)
        # TODO buttons for add, delete, modify, retrain, ....

        # set mode
        label_modus = QtGui.QLabel("Select modus:")
        self.layout.addWidget(label_modus)
        self.inactive_btn = QtWidgets.QRadioButton("Inactive")
        self.layout.addWidget(self.inactive_btn)

        self.training_btn = QtWidgets.QRadioButton("Training")
        self.training_btn.clicked.connect(self.handle_training)
        self.layout.addWidget(self.training_btn)

        self.prediction_btn = QtWidgets.QRadioButton("Prediction")
        self.prediction_btn.clicked.connect(self.handle_prediction)
        self.layout.addWidget(self.prediction_btn)
        
        self.ui.setLayout(self.layout)

    def ctrlWidget(self):
        return self.ui

    def set_recording(self, value):
        self.__is_recording == value

    def process(self, **kwds):
        if self.__state == ModusNode.TRAINING:
            self.train_model(kwds)

        if self.__state == ModusNode.PREDICTION:
            self.generate_prediction(kwds)

    def handle_prediction(self):
        print("predict")

    def handle_training(self):
        print("training started")

    def train_model(kwds):  # TODO
        pass

    def generate_prediction(kwds):  # TODO
        pass

fclib.registerNodeType(GestureNode, [('Data', )])


class FeatureExtractionNode(Node):
    nodeName = "FeatureExtraction"

    def __init__(self, name):
        terminals = {
            'in_x': dict(io='in'),
            'in_y': dict(io='in'),
            'in_z': dict(io='in'),
            'out': dict(io='out')
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        calc_x = np.fft.fft(kwds["in_x"])
        calc_y = np.fft.fft(kwds["in_y"])
        calc_z = np.fft.fft(kwds["in_z"])
        print("x: " + calc_x + ", " + "y: " + calc_y + ", " + "z: " + calc_z)
        return (calc_x, calc_y, calc_z)
        # TODO spectogramm

fclib.registerNodeType(FeatureExtractionNode, [('Data', )])


def createAndConnectNodes(chart):
    dippid_node = chart.createNode("DIPPID", pos=(0, 0))
    buffer_node_accel_x = chart.createNode("Buffer", pos=(100, -200))
    buffer_node_accel_y = chart.createNode("Buffer", pos=(130, -100))
    buffer_node_accel_z = chart.createNode("Buffer", pos=(100, 200))
    feature_extract_node = chart.createNode("FeatureExtraction", pos=(130, 100))
    activity_node = chart.createNode("ActivityRecognition", pos=(150, 0))

    chart.connectTerminals(
        dippid_node['accelX'], buffer_node_accel_x['dataIn'])
    chart.connectTerminals(
        dippid_node['accelY'], buffer_node_accel_y['dataIn'])
    chart.connectTerminals(
        dippid_node['accelZ'], buffer_node_accel_z['dataIn'])
    chart.connectTerminals(
        buffer_node_accel_x['dataOut'], feature_extract_node['in_x'])
    chart.connectTerminals(
        buffer_node_accel_y['dataOut'], feature_extract_node['in_y'])
    chart.connectTerminals(
        buffer_node_accel_z['dataOut'], feature_extract_node['in_z'])

    # TODO connect feature_extract_node['out']
    chart.connectTerminals(
        feature_extract_node['out'], activity_node['in'])

def setupWindow():
    win = QtGui.QMainWindow()
    win.setWindowTitle('Assignment 8')

    central_widget = QtGui.QWidget()
    win.setCentralWidget(central_widget)
    layout = QtGui.QGridLayout()
    central_widget.setLayout(layout)

    chart = Flowchart(terminals={'out': dict(io='out')})
    layout.addWidget(chart.widget(), 0, 0, 2, 1)
    
    createAndConnectNodes(chart)

    win.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())



if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.stdout.write("Please specify port")

    port = int(sys.argv[1])
    print(port)

    app = QtGui.QApplication([])
    
    setupWindow()

    sys.exit(app.exec_())
