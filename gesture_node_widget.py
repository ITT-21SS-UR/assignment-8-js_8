import pyqtgraph.flowchart.library as fclib

from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Qt import QtWidgets
from PyQt5.QtCore import pyqtSignal

from node_constants import NodeType, NodeDataType

class ManageGestureNodes(Node, QtGui.QWidget):
    nodeName = "ManageGestures"
    saved_gestures = []
    gesture_added = pyqtSignal()
    gesture_deleted = pyqtSignal()

    def __init__(self, name):
        super().__init__(name)
        self.setup_manage_gestures_ui()
        Node.__init__(self, name)
    
    def process(self, **kwds):
        pass
    
    def setup_manage_gestures_ui(self):
        self.ui = QtGui.QWidget()
        self.__layout = QtGui.QGridLayout()
        label_new_gesture = QtGui.QLabel("Create new gesture")

        self.__layout.addWidget(label_new_gesture)
        self.__gesture_name = QtGui.QLineEdit()
        self.__layout.addWidget(self.__gesture_name)

        self.add_btn = QtWidgets.QPushButton("Add")
        self.add_btn.clicked.connect(self.add_gesture)
        self.__layout.addWidget(self.add_btn)

        label_manage = QtGui.QLabel("Manage Gestures")
        self.__layout.addWidget(label_manage)

        self.selection_box = QtWidgets.QComboBox()
        self.selection_box.addItems(self.saved_gestures)
        #self.selection.currentIndexChanged.connect(self.selectionchange)
        self.__layout.addWidget(self.selection_box)

        self.del_btn = QtWidgets.QPushButton("Delete")
        #self.del_btn.clicked.connect(self.delete_gesture)
        self.__layout.addWidget(self.del_btn)

        self.retrain_btn = QtWidgets.QPushButton("Retrain")
        #self.retrain_btn.clicked.connect(self.delete_training_data)
        self.__layout.addWidget(self.retrain_btn)

        self.ui.setLayout(self.__layout)
        #self.setLayout(self.__layout)

    def ctrlWidget(self):
        return self.ui

    def add_gesture(self):
        self.saved_gestures.append(self.__gesture_name.text())
        self.__gesture_name.setText("")
        self.clear_list()
        self.selection_box.addItems(self.saved_gestures)

        self.gesture_added.emit()
        
        print(self.saved_gestures)

    def clear_list(self):
        for i in range(0, len(self.saved_gestures)):
            self.selection_box.removeItem(i)

    def delete_gesture(self):
        pass

fclib.registerNodeType(ManageGestureNodes, [('Data', )])