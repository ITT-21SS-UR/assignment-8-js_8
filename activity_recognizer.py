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

from svm_node import SVMNode

from node_constants import NodeType, NodeDataType

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
        #print("x: " + calc_x + ", " + "y: " + calc_y + ", " + "z: " + calc_z)
        #return (calc_x, calc_y, calc_z)
        # TODO spectogramm


fclib.registerNodeType(FeatureExtractionNode, [('Data', )])

class GestureNode(Node):
    nodeName = "GestureNode"

    def __init__(self, name):
        terminals = {
            'in_x': dict(io='in'),
            'in_y': dict(io='in'),
            'in_z': dict(io='in'),
            'out': dict(io='out')
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        pass

fclib.registerNodeType(GestureNode, [('Data', )])


class TextNode(Node):
    nodeName = "Prediction"

    def __init__(self, name):
        terminals = {
            'in_x': dict(io='in'),
            'in_y': dict(io='in'),
            'in_z': dict(io='in'),
            'out': dict(io='out')
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        pass


fclib.registerNodeType(TextNode, [('Data', )])


class MainWindow(QtGui.QMainWindow):
    def __init__(self, port_number=None):
        super(MainWindow, self).__init__()

        self.chart = Flowchart(terminals={'out': dict(io='out')})
        
        self.dippid_node = self.chart.createNode("DIPPID", pos=(0, 0))
        self.buffer_node_accel_x = self.chart.createNode("Buffer", pos=(100, -200))
        self.buffer_node_accel_y = self.chart.createNode("Buffer", pos=(130, -100))
        self.buffer_node_accel_z = self.chart.createNode("Buffer", pos=(100, 200))
        self.feature_extract_node = self.chart.createNode("FeatureExtraction", pos=(130, 100))
        self.svm_node = self.chart.createNode(SVMNode.nodeName, pos=(150, 0))

        self.setupWindow()

        # TODO
        # SVMNode.gesture_added.connect(self.add_new_nodes)

    def connect_nodes(self):
        # connect nodes
        self.chart.connectTerminals(
            self.dippid_node['accelX'], self.buffer_node_accel_x['dataIn'])
        self.chart.connectTerminals(
            self.dippid_node['accelY'], self.buffer_node_accel_y['dataIn'])
        self.chart.connectTerminals(
            self.dippid_node['accelZ'], self.buffer_node_accel_z['dataIn'])
        self.chart.connectTerminals(
            self.buffer_node_accel_x['dataOut'], self.feature_extract_node['in_x'])
        self.chart.connectTerminals(
            self.buffer_node_accel_y['dataOut'], self.feature_extract_node['in_y'])
        self.chart.connectTerminals(
            self.buffer_node_accel_z['dataOut'], self.feature_extract_node['in_z'])

        # TODO connect feature_extract_node['out']
        #chart.connectTerminals(
            #feature_extract_node['out'], svm_node['in'])

    def add_new_nodes(self):
        print("New node")
        node_list = SVMNode.saved_gestures
        for i in range(0, len(node_list)):
            gesture_node = self.chart.createNode("GestureNode", pos=(0, 0))
            gesture_node.nodeName = node_list[i]

            #self.chart.connectTerminals(
            #gesture_node['accel_x'], feature_extract_node['in_x'])
            #self.chart.connectTerminals(
            #gesture_node['accel_y'], feature_extract_node['in_y'])
            #self.chart.connectTerminals(
            #gesture_node['accel_z'], feature_extract_node['in_z'])


    def setupWindow(self):
        self.setWindowTitle('Assignment 8')

        central_widget = QtGui.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtGui.QGridLayout()
        central_widget.setLayout(layout)

        
        layout.addWidget(self.chart.widget(), 0, 0, 2, 1)
        
        self.connect_nodes()
        #SVMNode.gesture_added.connect(self.add_new_nodes)



if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.stdout.write("Please specify port")

    port = int(sys.argv[1])
    print(port)

    app = QtGui.QApplication([])
    main_win = MainWindow()

    # chart.nodes
    # chart.disconnectAll()
    # chart.removeNode()

    main_win.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())

    sys.exit(app.exec_())
