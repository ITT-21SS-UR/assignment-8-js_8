import pyqtgraph.flowchart.library as fclib

from enum import Enum
from PyQt5 import uic
from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Qt import QtWidgets
from PyQt5.QtCore import pyqtSignal
from sklearn import svm

from node_constants import NodeType, NodeDataType

class ModusNode(Enum): 
    TRAINING = 1
    PREDICTION = 2
    INACTIVE = 3


class SVMNode(Node, QtWidgets.QWidget):
    nodeName = NodeType.SVM_NODE.value
    saved_gestures = []

    def __init__(self, name):
        
        self.__state = ModusNode.INACTIVE
        self.__is_recording = False
        self.__classifier = svm.SVC(kernel='linear') # TODO correct one?

        self.setup_ui()

        terminals = {
            NodeDataType.DATA_IN.value: dict(io='in'), # TODO
            NodeDataType.DATA_OUT.value: dict(io='out')
        }
        Node.__init__(self, name, terminals=terminals)


    def setup_ui(self):
        self.ui = QtGui.QWidget()
        self.__layout = QtGui.QGridLayout()
        #self.layout = QtWidgets.QVBoxLayout

        # set mode
        label_modus = QtGui.QLabel("Select modus:")
        self.__layout.addWidget(label_modus)
        self.inactive_btn = QtWidgets.QRadioButton("Inactive")
        #self.inactive_btn.clicked.connect(self.handle_inactive_state)
        self.__layout.addWidget(self.inactive_btn)

        self.training_btn = QtWidgets.QRadioButton("Training")
        #self.training_btn.clicked.connect(self.handle_training_state)
        self.__layout.addWidget(self.training_btn)

        self.prediction_btn = QtWidgets.QRadioButton("Prediction")
        #self.prediction_btn.clicked.connect(self.handle_prediction_state)
        self.__layout.addWidget(self.prediction_btn)

        #self.setup_training_ui()
        #self.setup_prediction_ui()
        
        self.ui.setLayout(self.__layout)

    def setup_training_ui(self):
        label_training = QtGui.QLabel("Training")
        self.__layout.addWidget(label_training)
        self.selection_box = QtWidgets.QComboBox()
        
        #self.selection.currentIndexChanged.connect(self.selectionchange)
        self.__layout.addWidget(self.selection_box)

        self.start_btn = QtWidgets.QPushButton("Start")
        #self.start_btn.clicked.connect(self.start_training)
        self.__layout.addWidget(self.start_btn)

        self.stop_btn = QtWidgets.QPushButton("Stop")
        #self.stop_btn.clicked.connect(self.stop_training)
        self.__layout.addWidget(self.stop_btn)

    def setup_prediction_ui(self):
        label_prediction = QtGui.QLabel("Prediction")
        self.__layout.addWidget(label_prediction)

        self.start_btn = QtWidgets.QPushButton("Start")
        #self.start_btn.clicked.connect(self.start_prediction)
        self.__layout.addWidget(self.start_btn)

        self.predict_btn = QtWidgets.QPushButton("Stop && Predict")
        #self.predict_btn.clicked.connect(self.handle_prediction)
        self.__layout.addWidget(self.predict_btn)

    def delete_training_data():
        pass

    def start_training(kwds):
        pass

    def stop_training():
        pass

    def start_prediction(kwds):
        pass

    def generate_prediction(kwds):  # TODO
        pass

    def ctrlWidget(self):
        return self.ui

    def set_recording(self, value):
        self.__is_recording == value

    def process(self, **kwds):
        if self.__state == ModusNode.TRAINING:
            self.setup_training_ui()
            self.train_model(kwds)

        if self.__state == ModusNode.PREDICTION:
            self.setup_prediction_ui()
            self.generate_prediction(kwds)

    def handle_prediction_state(self):
        print("predict")

    def handle_training_state(self):
        self.setup_training_ui()
        print("training started")


fclib.registerNodeType(SVMNode, [('Data', )])