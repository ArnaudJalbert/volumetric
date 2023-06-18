from volumetric_imports import *


class Geometry(object):
    __slots__ = ("position", "material")

    def __init__(self, *, position=ZERO_POINT, material=None) -> None:
        """Init a material with provided information.
        If no arguments are provided the object will be at position (0,0,0) with the defautl material

        Args:
            position (Point, optional): Position of the geometry in the scene. Defaults to ZERO_POINT.
        """
        self.set_position(position)
        self.set_material(material)

    def __eq__(self, __value: object) -> bool:
        """Equal if the position and the material are equal.

        Args:
            __value (object): Geometry object to compare with.

        Returns:
            bool: True if the positions and materials are equal.
        """
        return (
            issubclass(__value.__class__, Geometry)
            and __value.position == self.position
            and __value.material == self.material
        )

    def set_position(self, position: Point):
        """Sets the position of the geometry in the scene.
        It is preferable to use this function since is performs tyoe checking instead of changing it directly.

        Args:
            position (Point): Point object of the position of the geometry.

        Raises:
            TypeError: The object must be a Point instance.
        """
        if not isinstance(position, Point):
            raise TypeError(
                "Expected an object of type {type}, but got {wrong_type}.".format(
                    Point.__name__, position.__class__.__name__
                )
            )
        self.position = position

    def set_material(self, material):
        """Sets the material of the geometry.
        It is preferable to use this function since is performs tyoe checking instead of changing it directly.

        Args:
            position (Point): Point object of the position of the geometry.

        Raises:
            TypeError: The object must be a Point instance.

        TODO:
        Implement this correctly once the Material object is implemented.
        """
        self.material = material

    def map(self, point: Point):
        """Estimates the distance between the point and the geometry.
        This function defines the geometry. It needs to be a 3D function that returns the distance from the point.
        It needs to be overriden by the concrete class.

        Args:
            point (Point): Current point on in 3D space.

        Returns:
            float: The approximate distance between the point and the geometry.
        """
        pass
