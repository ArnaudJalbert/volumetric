from PIL import Image

from scene import Scene
from camera import Camera
from point_light import PointLight
from sphere import Sphere
from vector import Vector
from volumetric import Volumetric

if __name__ == "__main__":
    # create the scene
    camera = Camera(width=500, height=500, fov=35)
    geometries = [
        Sphere(position=Vector([0, 0, -1]), radius=1.2),
    ]
    light = PointLight(position=Vector([1, 1, 1.5]))
    scene = Scene(camera=camera, geometries=geometries, light=light)
    volume = Volumetric(scene)
    buffer = volume.execute()

    # TODO: Make this class for renders

    # Create a new image with the given resolution
    image = Image.new("RGB", (scene.camera.width, scene.camera.height))

    # Set the pixel colors
    pixels = image.load()
    for y in range(scene.camera.width):
        for x in range(scene.camera.height):
            pixel_index = x * scene.camera.width + y
            pixels[x, y] = buffer[pixel_index]

    image.save("output.png")
