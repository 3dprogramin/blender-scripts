# Blender scripts

The blender scripts built for my own requirements.

Currently the repository contains only VSE scripts.

### List of scripts:

- **videos-compiler**
  -  Uses a predefined text file, in a simple format, containing timestamps from videos as well as root path and extensions allowed. The script will import the videos defined, in the order defined, and only the timestamps defined.
- **images-speed-up**
  - Make a video from a folder with images, each image staying for a specific amount of frames, while *important* images can be set to stay up longer (or shorter) frames.
- **scale-images**
  - Helpful when you import a bunch of images but they're either too small or too big for the screen. The script takes as input a list of image sizes (width and height) and a scale for each pair. Script goes through all the images in the scene and changes the scale of each image based on what was defined for that specific width and height.
- **misc**
  - Different (mostly simple) scripts that I used for figuring things out.