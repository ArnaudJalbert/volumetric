from dataclasses import dataclass, field
import math
from point import Point
from vector import Vector

DEFAULT_CAMERA_POSITION = lambda: Vector([0, 0, 5])
DEFAULT_LOOK_AT = lambda: Vector([0, 0, -1])
DEFAULT_LOOK_UP = lambda: Vector([0, 1, 0])
DEFAULT_FOV = 45
DEFAULT_WIDTH = 250
DEFAULT_HEIGHT = 250


@dataclass(kw_only=True, slots=True)
class Camera:
    position: Point = field(default_factory=DEFAULT_CAMERA_POSITION)
    look_at: Vector = field(default_factory=DEFAULT_LOOK_AT)
    look_up: Vector = field(default_factory=DEFAULT_LOOK_UP)
    width: int = field(default=DEFAULT_WIDTH)
    height: int = field(default=DEFAULT_HEIGHT)
    fov: float = field(default=DEFAULT_FOV)
    # to be computed when everything is set
    look_right: Vector = None
    aspect_ratio: float = None
    image_plane_height: float = None
    image_plane_width: float = None
    pixel_size: float = None
    half_pixel_size: float = None
    plane_top_left_corner: Point = None

    def init_camera_geometry(self):
        """Generates all the camera geometry.

        This needs to be set before generating rays from the camera.

        Normalizes look_at/look_up vectors
        Finds look right vector -> cross product of look_at and look_up.
        Sets aspect ration of the resolution -> width/height.

        Finds the image plane height and width.
        Finds the pizel size.
        Finds the top left corner of the image plane.

        Algorithm: https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-generating-camera-rays/generating-camera-rays.html
        """
        self.look_at.normalize()
        self.look_up.normalize()
        self.look_right = self.look_at ^ self.look_up

        self.aspect_ratio = float(self.width) / float(self.height)
        self.image_plane_height = math.tan((self.fov * 0.5) * (math.pi / 180)) * 2
        self.image_plane_width = self.image_plane_height * self.aspect_ratio
        self.pixel_size = self.image_plane_height / self.height
        self.half_pixel_size = self.pixel_size / 2

        self.plane_top_left_corner = (
            self.look_at
            + (self.look_up * (self.image_plane_height / 2.0))
            + (self.look_right * (-self.image_plane_width / 2.0))
        )

    def generate_ray_direction(self, position_x: int, position_y: int):
        """Generates a ray from the camera position that passes through
        the position_x and position_y pixel on the image plane

        Args:
            position_x (int): Position x of the pixel
            position_y (int): Position y of the pixel

        Returns:
            Vector: The ray direction that passes through the image plane at pixel in position_x and position_y
        """
        return (
            self.plane_top_left_corner
            + (self.look_right * (position_x * self.pixel_size) + self.half_pixel_size)
            - (self.look_up * (position_y * self.pixel_size) + self.half_pixel_size)
        ).normalized
