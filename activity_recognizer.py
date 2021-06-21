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

from DIPPID import SensorUDP, SensorSerial, SensorWiimote
from DIPPID_pyqtnode import BufferNode, DIPPIDNode

from svm_node import SVMNode
from gesture_node_widget import ManageGestureNodes
from node_constants import NodeType, NodeDataType

class FeatureExtractionNode(Node):
    nodeName = NodeType.FEATURE_EXTRACTION_NODE.value

    def __init__(self, name):
        terminals = {
            NodeDataType.ACCEL_X.value: dict(io='in'),
            NodeDataType.ACCEL_Y.value: dict(io='in'),
            NodeDataType.ACCEL_Z.value: dict(io='in'),
            NodeDataType.DATA_OUT.value: dict(io='out')
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        calc_x = np.fft.fft(kwds[NodeDataType.ACCEL_X.value])
        calc_y = np.fft.fft(kwds[NodeDataType.ACCEL_Y.value])
        calc_z = np.fft.fft(kwds[NodeDataType.ACCEL_Z.value])
        #print("x: " + calc_x + ", " + "y: " + calc_y + ", " + "z: " + calc_z)
        #return (calc_x, calc_y, calc_z)
        # TODO spectogramm


fclib.registerNodeType(FeatureExtractionNode, [('Data', )])

class GestureNode(Node):
    nodeName = NodeType.GESTURE_NODE.value

    def __init__(self, name):
        terminals = {
            NodeDataType.ACCEL_X.value: dict(io='in'),
            NodeDataType.ACCEL_Y.value: dict(io='in'),
            NodeDataType.ACCEL_Z.value: dict(io='in'),
            'out_x': dict(io='out_x'),
            'out_y': dict(io='out_y'),
            'out_z': dict(io='out_z')
        }
        Node.__init__(self, name, terminals=terminals)
    
    def process(self, **kwds):
        return 'out_x'

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
        
        self.dippid_node = self.chart.createNode(NodeType.DIPPID.value, pos=(0, 0))
        self.buffer_node_accel_x = self.chart.createNode(NodeType.BUFFER.value, pos=(100, -200))
        self.buffer_node_accel_y = self.chart.createNode(NodeType.BUFFER.value, pos=(130, -100))
        self.buffer_node_accel_z = self.chart.createNode(NodeType.BUFFER.value, pos=(100, 200))
        self.feature_extract_node = self.chart.createNode(NodeType.FEATURE_EXTRACTION_NODE.value, pos=(130, 100))
        self.svm_node = self.chart.createNode(SVMNode.nodeName, pos=(150, 0))
        #self.gesture_node = self.chart.createNode(NodeType.GESTURE_NODE.value, pos=(200, 0))


        self.management_node = self.chart.createNode("ManageGestures", pos=(10, 0))

        self.setupWindow()
        #self.__gesture_node_widget = GestureNodeGUI()
        #self.svm_node.gesture_added.connect(self.add_new_nodes)
        #self.__gesture_node_widget.gesture_added.connect(self.add_new_nodes)
        self.management_node.gesture_added.connect(self.add_new_nodes)

        

    def connect_nodes(self):
        # connect nodes
        self.chart.connectTerminals(
            self.dippid_node['accelX'], self.buffer_node_accel_x['dataIn'])
        self.chart.connectTerminals(
            self.dippid_node['accelY'], self.buffer_node_accel_y['dataIn'])
        self.chart.connectTerminals(
            self.dippid_node['accelZ'], self.buffer_node_accel_z['dataIn'])
        self.chart.connectTerminals(
            self.buffer_node_accel_x['dataOut'], self.feature_extract_node[NodeDataType.ACCEL_X.value])
        self.chart.connectTerminals(
            self.buffer_node_accel_y['dataOut'], self.feature_extract_node[NodeDataType.ACCEL_Y.value])
        self.chart.connectTerminals(
            self.buffer_node_accel_z['dataOut'], self.feature_extract_node[NodeDataType.ACCEL_Z.value])

        # TODO connect feature_extract_node['out']
        #chart.connectTerminals(
            #feature_extract_node['out'], svm_node['in'])

    def add_new_nodes(self):
        print("New node")
        # TODO nodeName == Texteingabe
        new_node = self.chart.createNode("GestureNode", pos=(0, 0))
        new_node.nodeName = "Test"

        # TODO connection
        self.chart.update()

    def setupWindow(self):
        self.setWindowTitle('Assignment 8')

        central_widget = QtGui.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtGui.QGridLayout()
        central_widget.setLayout(layout)
        
        layout.addWidget(self.chart.widget(), 0, 0, 2, 1)
        
        self.connect_nodes()


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
