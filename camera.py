from volumetric_imports import *


class Camera(object):
    __slots__ = ("position", "look_at", "look_up", "fov")

    def __init__(
        self,
        *,
        position=ZERO_POINT,
        look_at=DEFAULT_LOOK_AT,
        look_up=DEFAULT_LOOK_UP,
        fov=DEFAULT_FOV
    ) -> None:
        pass
