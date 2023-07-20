from PIL import Image
from vector import Vector

from scene import Scene
from sphere import Sphere
from volumetric import volumetric

if __name__ == "__main__":
    # create the scene
    scene = Scene()
    scene.geometries.append(Sphere(position=Vector([-1, -1, -1]), color=(52, 52, 52)))
    volume = volumetric(scene)
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
