import numpy as np
import math
from pyrr import Vector3 as Point
from pyrr import Vector3 as Vector

# common default values
ZERO_POINT = lambda: Point([0, 0, 0])

# default resolution values
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080

# default camera factories and values
DEFAULT_LOOK_AT = lambda: Vector([0, 0, -1])
DEFAULT_LOOK_UP = lambda: Vector([0, 1, 0])
DEFAULT_FOV = 45

# default sphere values
DEFAULT_RADIUS = 1
