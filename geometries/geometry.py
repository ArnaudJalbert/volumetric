from abc import abstractmethod, ABC
from pyrr import Vector3, Vector4


class Geometry(ABC):

    def __init__(self, color=Vector4([1., 1., 1., 1.])):
        self.color = color

    @abstractmethod
    def map(self, p: Vector3) -> float:
        pass
