# github.com/3dprogramin
# ****************************

from datetime import datetime
import os
import bpy

# **********************************************************************
# SETTINGS
# **********************************************************************
# general
# ---------------------------
CLEAR_SCENE = True
# images
# --------------------------
# folder with images
IMAGE_FOLDER_PATH = "/home/icebox/Desktop/pictures"
# accepted image extensions
IMAGE_EXTENSIONS = ['png', 'jpg']
# how many frames / picture
FRAMES_PER_PIC = 10
FRAMES_PER_PIC_IMPORTANT = 150
# scale of images
SCALE_PIC_X = 0.3125
SCALE_PIC_Y = 0.3125
# important images text file
IMPORTANT_IMAGES_PATH = '/home/icebox/Desktop/pictures/important.txt'
# rendering
# ---------------------------
FPS = 60
# render after project is build
RENDER = False

# END SETTINGS, DO NOT EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# **********************************************************************


# find sequence editor
def find_sequence_editor():
    for area in bpy.context.window.screen.areas:
        if area.type == "SEQUENCE_EDITOR":
            return area
    return None


# clear the sequencer for any items
def clean_sequencer(sequence_context):
    sequence_context = {"area": find_sequence_editor()}
    bpy.ops.sequencer.select_all(sequence_context, action="SELECT")
    bpy.ops.sequencer.delete(sequence_context)


# get the image files from folder
def get_image_files(image_folder_path):
    image_files = list()
    for file_name in os.listdir(image_folder_path):
        s = file_name.lower().split('.')
        # check if it has extension
        if len(s) < 2:
            continue
        
        if s[-1] in IMAGE_EXTENSIONS:
            image_files.append(file_name)
    image_files.sort()

    return image_files


# get dimensions of image
def get_image_dimensions(image_path):
    image = bpy.data.images.load(image_path)
    width, height = image.size
    return width, height


# set render scene parameters
def set_up_output_params(image_folder_path, image_files, fps):
    frame_count = len(image_files)

    scene = bpy.context.scene

    # print(image_files)
    image_path = os.path.join(image_folder_path, image_files[0])

    width, height = get_image_dimensions(image_path)

#    scene.render.resolution_y = height
#    scene.render.resolution_x = width

    scene.render.fps = fps
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"

    now = datetime.now()
    time = now.strftime("%H-%M-%S")
    filepath = os.path.join(image_folder_path, f"anim_{time}.mp4")
    scene.render.filepath = filepath


# generate the video using the settings given
def gen_video_from_images(image_folder_path, fps, index=0):
    # get the image files from folder
    image_files = get_image_files(image_folder_path)
    print(f'All images: {len(image_files)}')

    # set params
    set_up_output_params(image_folder_path, image_files, fps)
    
    # clear the sequencer
    if CLEAR_SCENE:
        clean_sequencer(find_sequence_editor())
        
    # get the important images (names)
    important_images = get_important_images()
    print(f'Important images: {len(important_images)}')

    file_info = list()
    k = bpy.data.scenes['Scene'].frame_current
    
    # go through images
    for image_name in image_files:
        # check if image is important / partial match
        is_important = False
        for e in important_images:
            if e in image_name:
                is_important = True
                # print("IS IMPORTANT", image_name)
            # break
        
        frame_end = k + FRAMES_PER_PIC
        # if image is important, allocate more frames for it
        if is_important:
            frame_end = k + FRAMES_PER_PIC_IMPORTANT

        sequence_context = {"area": find_sequence_editor()}
        bpy.ops.sequencer.image_strip_add(sequence_context, directory=image_folder_path + os.sep, files=[{"name":image_name, "name":image_name}], frame_start=k, frame_end=frame_end, channel=1, fit_method='FIT')
        bpy.context.scene.sequence_editor.sequences_all[image_name].transform.scale_x = SCALE_PIC_X
        bpy.context.scene.sequence_editor.sequences_all[image_name].transform.scale_y = SCALE_PIC_Y
       
        # different frame rates if important
        if is_important:
            k += FRAMES_PER_PIC_IMPORTANT
        else:
            k += FRAMES_PER_PIC
    if RENDER:
        bpy.ops.render.render(animation=True)

# get the important images from file (those that will play more frames)
def get_important_images():
    images = []
    with open(IMPORTANT_IMAGES_PATH, 'r') as f:
        for line in f:
            line = line.split('#')[0].strip()
            if line:
                images.append(line)
    return images
    

# main method, generate video from images, with given FPS
def main():
    print('Script started')
    gen_video_from_images(IMAGE_FOLDER_PATH, FPS)
    print('Finished !')

if __name__ == "__main__":
    main()
