import bpy
import os
from PIL import Image

# settings
# ---------------------
IMAGE_PATH = '/home/icebox/Documents/programming/blender/images/phone'

# how to scale images
# [width, height]: scale (width and height)
IMAGE_SCALES = {
    '[3072, 4096]': 0.371,
    '[4096, 3072]': 0.495,
    '[4896, 6528]': 0.234,
    '[4000, 3000]': 0.507,
    '[6528, 4896]': 0.311,
    '[3840, 2592]': 0.588,
    '[1512, 1512]': 1
}


# get the image size
def get_image_size(image):
    full_path = os.path.join(IMAGE_PATH, image)
    # print(full_path)
    with Image.open(full_path) as im:
        width, height = im.size
        return f'[{width}, {height}]'

# scale image
def scale_image(image, value):
    # read the horizontal images
    bpy.context.scene.sequence_editor.sequences_all[image].transform.scale_x = value
    bpy.context.scene.sequence_editor.sequences_all[image].transform.scale_y = value


def main():
    # get images from scene
    scene_images = [x.name for x in bpy.context.scene.sequence_editor.sequences_all]
    print(f'Got {len(scene_images)} images from scene')
    
    # get image sizes and change their scale
    for image in scene_images:
        size = get_image_size(image)
        if size in IMAGE_SCALES.keys():
            scale_image(image, IMAGE_SCALES[size])
        else:
            print(f'WARNING: unknown size for image: {image} - {size}')
            # raise Exception(f'unknown size for image: {image} - {size}')
            
    print('Completed !')
        
    
main()
