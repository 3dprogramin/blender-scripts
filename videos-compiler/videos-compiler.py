# github.com/3dprogramin
# ****************************

import os, bpy
from time import sleep

# set FPS for video
FPS = 60
# this matters if end is used in the preset text file for scenes
# 05:19 is for GoPro Hero 8
VIDEOS_LENGTH = '05:19'

# for title and subtitle at start
EXTRA_PROCESSING = True
TITLE = '[Motocross]'
SUBTITLE = "Spre Maramu'"

class ConfigParser:
    def __init__(self) -> None:
        self.items = []
        
    # check if file exists, and with what extension
    def _parse_file_with_extensions(self, path: str, extensions: list):
        for ext in extensions:
            f = path + '.' + ext
            f1 = path + '.' + ext.upper()
            if os.path.exists(f):
                return f
            if os.path.exists(f1):
                return f1
        return None
    
    # parse scene timestamps
    # returns both text and seconds if success
    # otherwise None
    def _parse_scene_timestamps(self, start: str, end: str):
        start = start.strip()
        end = end.strip()
        if start.lower() == 'start':
            start = '00:00'
        if end.lower() == 'end':
            end = VIDEOS_LENGTH
        
        # validate that it's a correct time
        start_s = start.split(':')
        if len(start_s) != 2 or any([x for x in start_s if len(x) != 2]) :
            return None
        end_s = end.split(':')
        if len(end_s) != 2 or any([x for x in end_s if len(x) != 2]) :
            return None
        
        
        # start part
        start_seconds = 0
        start_left = start_s[0].lstrip('0')
        if start_left != '':
            start_seconds += int(start_left) * 60

        start_right = start_s[1].lstrip('0')            
        if start_right:
            start_seconds += int(start_right)
        
        # end part
        end_seconds = 0
        end_left = end_s[0].lstrip('0')
        if end_left != '':
            end_seconds += int(end_left) * 60

        end_right = end_s[1].lstrip('0')            
        if end_right:
            end_seconds += int(end_right)
        
        
        return dict(start=start_seconds, end=end_seconds, start_s=start, end_s=end)
        
    # parse the config file
    def parse_file(self, config_path: str):
        items = []
        # check if file exists
        if not os.path.exists(config_path):
            raise Exception(f'config file does not exist: {config_path}')
        
        # set default as root
        root_path = os.getcwd()
        # set default extensions
        extensions = ['mp4', 'mov', 'avi']
        
        line_no = 0
        # read the file
        with open(config_path) as f:
            for line in f:
                line_no += 1
                original_line = line
                # strip line
                line = line.strip()
                # check for comments
                if line.startswith('#'):
                    continue
                
                # trim comments
                line = line.split('#')[0]
                
                # check if we have a video section
                if line.startswith('%%'):                    
                    # we do
                    # parse the line
                    l = line.split('-')
                    if len(l) != 3:
                        raise Exception(f'line #{line_no} has invalid format: {original_line}')
                    
                    # generate absolute file path
                    filename = os.path.join(root_path, l[0].replace('%%', '').strip())
                    filename = self._parse_file_with_extensions(filename, extensions)
                    # check if it exists
                    if not filename:
                        raise Exception(f'line #{line_no} file that does not exist: {filename}[{extensions}]')
                    
                    # parse timestamps
                    timestamp = self._parse_scene_timestamps(l[1], l[2])
                    # check if it exists
                    if not timestamp:
                        raise Exception(f'line #{line_no} invalid timestamps: {original_line}')
                    
                    # we have a valid one
                    items.append(dict(full_path=os.path.join(root_path, filename), timestamp=timestamp))
                elif line.startswith('%'):
                    # we have settings
                    if line.lower().startswith('%path'):
                        root_path = line.replace('%path', '').lstrip('=')
                    elif line.lower().startswith('%path'):
                        extensions = [x.replace('.', '') for x in line.replace('%extensions', '').split(',')]
        
        return items
        
class Blender:
    @staticmethod
    def find_sequence_editor():
        for area in bpy.context.window.screen.areas:
            if area.type == "SEQUENCE_EDITOR":
                return area
        return None
            
    @staticmethod
    def clean_sequencer(sequence_context, delete_only=False):
        if not delete_only:
            bpy.ops.sequencer.select_all(sequence_context, action="SELECT")
        bpy.ops.sequencer.delete(sequence_context)

    # selects all elements from specific channel
    @staticmethod
    def select_all_from_channel(active_channel: int = 2):
        context = bpy.context
        scene = context.scene

        sed = scene.sequence_editor
        # if active strip isn't in active_channel set to None.
        if getattr(sed.active_strip, "channel", -1) != active_channel:
            sed.active_strip = None

        sequences = sed.sequences_all
        # select all strips in active channel
        for strip in sequences:
            strip.select = strip.channel == active_channel
    
    @staticmethod
    def get_first_clip(channel: int = 1, last = False):
        context = bpy.context
        scene = context.scene

        sed = scene.sequence_editor
        # if active strip isn't in active_channel set to None.
        if getattr(sed.active_strip, "channel", -1) != channel:
            sed.active_strip = None

        sequences = sed.sequences_all
        # select all strips in active channel
        for strip in sequences:
            if strip.channel == channel:
                if not last:
                    return strip
        # return the last one    
        return strip

    @staticmethod
    def get_clip(name):
        context = bpy.context
        scene = context.scene

        sed = scene.sequence_editor
        sequences = sed.sequences_all
        # select all strips in active channel
        for strip in sequences:
            if strip.name == name:
                return strip
                
        raise Exception('could not find clip by name: ' + name)

    @staticmethod
    def get_title_subtitle():
        context = bpy.context
        scene = context.scene

        sed = scene.sequence_editor

        t = {}
        sequences = sed.sequences_all
        # select all strips in active channel
        for strip in sequences:
            if strip.channel == 6:
                t['title'] = strip
            elif strip.channel == 5 and 'subtitle' not in t:        
                t['subtitle'] = strip
        return t
        
    
class App:
    # cut the video, 3 different cases
    # - cut one time
    # - cut two times
    # - no cut
    @staticmethod
    def cut_video(scene):
        # clear 
        Blender.select_all_from_channel(4)
        
        # check which case we're in
        start = scene['timestamp']['start']
        end = scene['timestamp']['end']
        
        # full video
        if start == 0 and end == 319:
            # no split, pass
            pass
        elif start == 0 or end == 319:
            # on cut
            cut_frame = start * FPS if start !=0 else end * FPS
            side = 'LEFT' if start == 0 else 'RIGHT'
            bpy.ops.sequencer.split(frame=cut_frame, channel=4, type='SOFT', side=side)
        else:
            # two cuts
            bpy.ops.sequencer.split(frame=start * FPS, channel=4, type='SOFT', side='RIGHT')
            bpy.ops.sequencer.split(frame=end * FPS, channel=4, type='SOFT', side='LEFT')

    @staticmethod
    def get_cut_offset(move_object_only=False):
        move_object_frame_start = None
        last_object_first_channel = None
        
        # get the start frame for the strip that has to be move
        for strip in bpy.context.scene.sequence_editor.sequences:
            if strip.select and strip.channel == 4:
                move_object_frame_start = strip.frame_final_start
                if move_object_only:
                    if 'GH0' in strip.name:
                        return None
                    return move_object_frame_start * -1 + 1
                break

        # get the end frame of last strip from channel 1 
        for strip in bpy.context.scene.sequence_editor.sequences:
            if strip.channel == 1:
                last_object_first_channel = strip.frame_final_end
        
        # calculate based on positions
        if move_object_frame_start > last_object_first_channel:
            x = (move_object_frame_start - last_object_first_channel) * -1
        else:
            x = last_object_first_channel - move_object_frame_start - 1
        return x

def main():        
    c = ConfigParser()
    scenes = c.parse_file('/home/icebox/Desktop/example.txt')

    # clear the sequencer of all objects on working channels
    for i in range(1, 5):
        Blender.select_all_from_channel(i)
        Blender.clean_sequencer({"area": Blender.find_sequence_editor()}, delete_only=True)
    
    # add scenes
    i = 1
    
    for scene in scenes:
        sequence_editor_context = {"area": Blender.find_sequence_editor()}
        filename = os.path.basename(scene['full_path'])

        print(f'Video path: {scene["full_path"]}')

        # clear the channel 4
        Blender.select_all_from_channel(4)
        Blender.clean_sequencer(sequence_editor_context, delete_only=True)
        
        # add movie strip (with audio) 
        bpy.ops.sequencer.movie_strip_add(sequence_editor_context, filepath=scene['full_path'], directory=os.path.dirname(scene['full_path']), files=[{"name":filename, "name":filename}], show_multiview=False, frame_start=1, channel=3, fit_method='FIT', set_view_transform=False, use_framerate=False)
        
        # combine them
        bpy.ops.sequencer.meta_make()
        
        # cut the new movie strip added
        App.cut_video(scene)
        frame_offset = App.get_cut_offset(move_object_only=True if i == 1 else False)

        if i == 1:
            # if it's the first one, add to channel 1, frame 1
            bpy.ops.transform.seq_slide(sequence_editor_context, value=(frame_offset, -3), orient_axis_ortho='X', view2d_edge_pan=True)
        else:
            # with context.temp_override():
            bpy.ops.transform.seq_slide(sequence_editor_context, value=(frame_offset, -3), orient_axis_ortho='X', view2d_edge_pan=True)
        # print('frame offset', frame_offset)
        
        Blender.select_all_from_channel(4)
        Blender.clean_sequencer(sequence_editor_context, delete_only=True)
        i += 1
    
    
    # ---------------------------------------
    # the video is built at this point
    # but we are doing some extra processing
    # changing some text, blend, etc
    # ---------------------------------------
    if EXTRA_PROCESSING:
        # set title and subtitle
        # -----------------------------------------------------
        strips = Blender.get_title_subtitle()
        strips['title'].text = TITLE
        strips['subtitle'].text = SUBTITLE
        
        # create blend for first video
        # -----------------------------------------------------
        first_clip = Blender.get_clip('MetaStrip.001')
        #print('first clip', first_clip)
        #print(first_clip.name)
        
        # make it 0 at first
        first_clip.blend_alpha = 0
        first_clip.keyframe_insert("blend_alpha", frame=100)

        first_clip.blend_alpha = 100
        first_clip.keyframe_insert("blend_alpha", frame=400)    
        
        
        # set end frame (not working yet)
        # ----------------------------------
        #last_clip = Blender.get_first_clip(last=True)
        #print('final frame', last_clip.frame_final_end)
        #bpy.context.scene.frame_end = last_clip.frame_final_end
    
    

if __name__ == "__main__":
    print('Script started')
    main()
    print('Finished !')
