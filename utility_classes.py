from enum import Enum


class Detector(Enum):
    NONE = 0
    RGB = 1
    FAN = 2
    BUZZER = 3


class Colors(Enum):
    CYAN = (19, 169, 214)
    BLUE_GREEN = (9, 227, 158)
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    PURPLE = (152, 19, 214)
