#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np
from sklearn import svm
import DIPPID_pyqtnode
from enum import Enum

class FftNode(Node):
    nodeName = "Fft"
    
    SAMPLE_SIZE = 64

    def __init__(self, name):
        terminals = { "accelX": { "io": "in" },
                      "accelY": { "io": "in" },
                      "accelZ": { "io": "in" },
                      "dspOut": { "io": "out" } }
        super().__init__(name, terminals)

        self.clear()

    def clear(self):
        self.__avg = []

    def process(self, **kargs):
        x, y, z = kargs["accelX"], kargs["accelY"], kargs["accelZ"]

        if len(self.__avg) > FftNode.SAMPLE_SIZE:
            pos = len(self.__avg) - FftNode.SAMPLE_SIZE + len(x)
            self.__avg = self.__avg[pos:]

        for i in range(len(x)):
            self.__avg.append((x[i] + y[i] + z[i]) / 3)
        
        windowed = np.hamming(len(self.__avg)) * self.__avg
        freq = np.fft.fft(windowed, FftNode.SAMPLE_SIZE) / len(windowed)
        amplitude_spectrum = np.abs(freq)[1:len(freq) // 2]
        return { "dspOut": amplitude_spectrum }
        
fclib.registerNodeType(FftNode, [("DSP",)])

class SvmNodeCtrl(QtGui.QWidget):

    class SvmMode(Enum):
        Inactive = 1
        Training = 2
        Prediction = 3

    training_started = QtCore.pyqtSignal()
    data_changed = QtCore.pyqtSignal()
    mode_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__mode = SvmNodeCtrl.SvmMode.Inactive
        self.__setup_ui()

        self.__data = {}

    def get_mode(self):
        return self.__mode

    def get_categories(self):
        categories = []

        for i in range(self.__cat_list.count()):
            categories.append(self.__cat_list.itemText(i))

        return categories

    def get_category_name(self, index=None):
        if index is None:
            return self.__cat_list.currentText()

        return self.__cat_list.itemText(index)

    def get_all_data(self):
        return self.__data

    def get_data(self):
        if not self.__data:
            return []

        return self.__data[self.get_category_name()]

    def set_data(self, data):
        if len(data) > 0:
            self.__data[self.get_category_name()].append(data)

        self.__update_training_buttons()

    def __setup_ui(self):
        layout = QtWidgets.QVBoxLayout()

        mode_group = QtWidgets.QGroupBox("Mode")
        inactive_button = QtWidgets.QRadioButton("Inactive", mode_group)
        inactive_button.setChecked(True)
        training_button = QtWidgets.QRadioButton("Training", mode_group)
        prediction_button = QtWidgets.QRadioButton("Prediction", mode_group)
        mode_group_layout = QtWidgets.QVBoxLayout()
        mode_group_layout.addWidget(inactive_button)
        mode_group_layout.addWidget(training_button)
        mode_group_layout.addWidget(prediction_button)
        mode_group.setLayout(mode_group_layout)

        categories_group = QtWidgets.QGroupBox("Categories")
        cat_name_edit = QtWidgets.QLineEdit()
        cat_name_label = QtWidgets.QLabel("New category name")
        cat_name_label.setBuddy(cat_name_edit)
        cat_add_button = QtWidgets.QToolButton()
        cat_add_button.setText("+")
        cat_name_layout = QtWidgets.QHBoxLayout()
        cat_name_layout.addWidget(cat_name_edit)
        cat_name_layout.addWidget(cat_add_button)
        cat_list = QtWidgets.QComboBox()
        train_button = QtWidgets.QPushButton("Train")
        train_button.setEnabled(False)
        train_button.setCheckable(True)
        reset_button = QtWidgets.QPushButton("Reset")
        reset_button.setEnabled(False)
        delete_button = QtWidgets.QPushButton("Delete")
        delete_button.setEnabled(False)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(reset_button)
        button_layout.addWidget(delete_button)
        categories_group_layout = QtWidgets.QVBoxLayout()
        categories_group_layout.addWidget(cat_name_label)
        categories_group_layout.addLayout(cat_name_layout)
        categories_group_layout.addWidget(cat_list)
        categories_group_layout.addWidget(train_button)
        categories_group_layout.addLayout(button_layout)
        categories_group.setLayout(categories_group_layout)

        layout.addWidget(mode_group)
        layout.addWidget(categories_group)

        self.setLayout(layout)
        self.__cat_list = cat_list
        self.__cat_name_edit = cat_name_edit
        self.__train_button = train_button
        self.__reset_button = reset_button
        self.__delete_button = delete_button

        inactive_button.clicked.connect(self.__on_mode_changed)
        training_button.clicked.connect(self.__on_mode_changed)
        prediction_button.clicked.connect(self.__on_mode_changed)
        cat_add_button.clicked.connect(self.__on_add_category)
        delete_button.clicked.connect(self.__on_delete_category)
        train_button.clicked.connect(self.__on_train_clicked)
        reset_button.clicked.connect(self.__clear_data)

    def __on_mode_changed(self):
        if self.sender().text() == "Inactive":
            self.__mode = SvmNodeCtrl.SvmMode.Inactive

        if self.sender().text() == "Training":
            self.__mode = SvmNodeCtrl.SvmMode.Training

        if self.sender().text() == "Prediction":
            self.__mode = SvmNodeCtrl.SvmMode.Prediction

        self.__update_training_buttons()
        self.mode_changed.emit()

    def __on_add_category(self):
        name = self.__cat_name_edit.text()
        if not name:
            return

        if self.__cat_list.findText(name, QtCore.Qt.MatchFixedString) >= 0:
            return

        self.__cat_name_edit.setText("")
        self.__cat_list.addItem(name)
        self.__cat_list.setCurrentIndex(self.__cat_list.count() - 1)
        self.__data[name] = []
        self.__update_training_buttons()

    def __on_delete_category(self):
        self.__data.pop(self.get_category_name())
        self.__cat_list.removeItem(self.__cat_list.currentIndex())
        self.__update_training_buttons()
        self.data_changed.emit()

    def __update_training_buttons(self):
        self.__delete_button.setEnabled(self.__cat_list.count() > 0)

        can_enable_reset_btn = self.__cat_list.count() > 0 \
                                    and len(self.get_data()) > 0 \
                                    and self.__mode == SvmNodeCtrl.SvmMode.Training
        self.__reset_button.setEnabled(can_enable_reset_btn)

        can_enable_training_btn = self.__cat_list.count() > 0 \
                                    and self.__mode == SvmNodeCtrl.SvmMode.Training
        self.__train_button.setEnabled(can_enable_training_btn)

    def __on_train_clicked(self, checked):
        if checked:
            self.__train_button.setText("Training...")
            self.training_started.emit()
        else:
            self.__train_button.setText("Train")
            self.data_changed.emit()

    def __clear_data(self):
        self.__data[self.get_category_name()] = []
        self.__update_training_buttons()


class SvmNode(Node):
    nodeName = "SVM"

    def __init__(self, name):
        terminals = { "dspIn": { "io": "in" },
                      "categoryOut": { "io": "out" } }
        super().__init__(name, terminals)

        self.__buffer = []
        self.__classifier = svm.SVC()
        
        self.ui = SvmNodeCtrl()
        self.ui.training_started.connect(self.__clear_buffer)
        self.ui.data_changed.connect(self.__process_training_data)
        self.ui.mode_changed.connect(self.__clear_buffer)

    def ctrlWidget(self):
        return self.ui

    def process(self, **kargs):
        if self.ui.get_mode() == SvmNodeCtrl.SvmMode.Inactive:
            return { "categoryOut": "** classifier inactive **" }

        self.__buffer = kargs["dspIn"]

        if self.ui.get_mode() == SvmNodeCtrl.SvmMode.Training:
            return { "categoryOut": "** training mode **" }

        if len(self.ui.get_categories()) < 2:
            return { "categoryOut": "** you have to train at least 2 categories **"}

        try:
            category = self.__classifier.predict([self.__buffer])
            return { "categoryOut": self.ui.get_category_name(category[0]) }
        except ValueError:
            return { "categoryOut": "** need more training data **" }

    def __process_training_data(self):
        self.ui.set_data(self.__buffer)
        self.__clear_buffer()
        self.__train_data()

    def __clear_buffer(self):
        self.__buffer = []

    def __train_data(self):
        training_set = []
        classifiers = []

        categories = self.ui.get_categories()
        all_data = self.ui.get_all_data()

        for i in range(len(categories)):
            category_name = self.ui.get_category_name(i)
            data = all_data[category_name]
            
            for d in data:
                training_set.append(d)
                classifiers.append(i)

        try:
            self.__classifier.fit(training_set, classifiers)
        except ValueError:
            pass

fclib.registerNodeType(SvmNode, [("Classifier",)])

class TextDisplayNode(Node):
    nodeName = "TextDisplay"

    def __init__(self, name):
        terminals = { "textIn": { "io": "in" } }
        super().__init__(name, terminals)

        self.__text = None

    def get_text(self):
        return self.__text

    def set_text(self, text):
        self.__text = text

    def process(self, **kargs):
        if self.__text is not None:
            self.__text.setText(kargs["textIn"])

        return {}

fclib.registerNodeType(TextDisplayNode, ("Display",))

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Activity Recognizer")

        self.__fc = Flowchart()

        layout = QtGui.QGridLayout()
        layout.addWidget(self.__fc.widget(), 0, 0, 2, 1)
        text = QtWidgets.QLabel("** predicted category will be shown here**")
        layout.addWidget(text, 0, 1)

        cw = QtGui.QWidget()
        cw.setLayout(layout)
        self.setCentralWidget(cw)

        self.__categoryText = text
        self.__setup_nodes()

    def __setup_nodes(self):
        dippid_node = self.__fc.createNode("DIPPID", pos=(0, 0))
        buf_x = self.__fc.createNode("Buffer", pos=(150, -50))
        buf_y = self.__fc.createNode("Buffer", pos=(150, 0))
        buf_z = self.__fc.createNode("Buffer", pos=(150, 50))
        dsp_node = self.__fc.createNode("Fft", pos=(300, 50))
        svm_node = self.__fc.createNode("SVM", pos=(450, 0))
        display = self.__fc.createNode("TextDisplay", pos=(450, -50))
        display.set_text(self.__categoryText)

        self.__fc.connectTerminals(dippid_node["accelX"], buf_x["dataIn"])
        self.__fc.connectTerminals(dippid_node["accelY"], buf_y["dataIn"])
        self.__fc.connectTerminals(dippid_node["accelZ"], buf_z["dataIn"])
        self.__fc.connectTerminals(buf_x["dataOut"], dsp_node["accelX"])
        self.__fc.connectTerminals(buf_y["dataOut"], dsp_node["accelY"])
        self.__fc.connectTerminals(buf_z["dataOut"], dsp_node["accelZ"])
        self.__fc.connectTerminals(dsp_node["dspOut"], svm_node["dspIn"])
        self.__fc.connectTerminals(svm_node["categoryOut"], display["textIn"])

        svm_node.ctrlWidget().training_started.connect(lambda: dsp_node.clear())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
