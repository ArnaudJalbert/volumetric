import unittest
import logging

from volumetric_imports import *
from geometry import Geometry
from sphere import Sphere


class GeometryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test_geometry = Geometry(position=Point([1, 2, 3]))
        self.same_test_geometry = Geometry(position=Point([1, 2, 3]))
        self.different_test_geometry = Geometry(position=Point([3, 2, 1]))

        self.test_sphere = Sphere(radius=1.0, position=Point([0, 0, 0]))
        self.same_test_sphere = Sphere(radius=1.0, position=Point([0, 0, 0]))
        self.different_test_sphere = Sphere(radius=2.0)

        self.logger = logging.getLogger("Geometry Test")

    def test_geometry_equality(self):
        self.logger.info("Geometry Equality Test")
        self.assertEqual(self.test_geometry, self.same_test_geometry)
        self.assertNotEqual(self.test_geometry, self.different_test_geometry)

    def test_geometry_position(self):
        self.logger.info("Geometry Position Test")
        self.assertEqual(self.test_geometry.position.x, 1)
        self.assertEqual(self.test_geometry.position.y, 2)
        self.assertEqual(self.test_geometry.position.z, 3)

    def test_sphere_radius(self):
        self.logger.info("Sphere Radius Test")
        self.assertEqual(self.test_sphere.radius, 1)

    def test_sphere_equality(self):
        self.logger.info("Sphere Equality Test")
        self.assertEqual(self.test_sphere, self.same_test_sphere)
        self.assertNotEqual(self.test_sphere, self.different_test_sphere)

    def test_sphere_map(self):
        self.logger.info("Sphere Equality Test")
        self.assertEqual(self.test_sphere.map(Point([0, 0.5, 0])), 0)
        self.assertEqual(self.test_sphere.map(Point([0, 1, 0])), 0)
        self.assertEqual(self.test_sphere.map(Point([0, 2, 0])), 1)
        self.assertEqual(self.test_sphere.map(Point([2, 0, 0])), 1)
        self.assertEqual(self.test_sphere.map(Point([5, 0, 0])), 4)
        self.assertEqual(self.different_test_sphere.map(Point([5, 0, 0])), 3)


if __name__ == "__main__":
    unittest.main()
