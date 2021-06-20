from enum import Enum
class NodeType(Enum):
    DIPPID = "DIPPID"
    BUFFER = "Buffer"
    FEATURE_EXTRACTION_NODE = "FeatureExtractionNode"
    SVM_NODE = "SVM_Node"
    GESTURE_NODE = "GestureNode"
    TEXT_NODE = "textNode"


class NodeDataType(Enum):  #
    DATA_IN = "In"
    DATA_OUT = "Out"
    ACCEL_X = "accelX"
    ACCEL_Y = "accelY"
    ACCEL_Z = "accelZ"
    SPECTROGRAM = "spectogramm"
    