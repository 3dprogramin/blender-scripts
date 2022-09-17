import bpy

print()
print()
print()

context = bpy.context
scene = context.scene

active_channel = 2

sed = scene.sequence_editor
# if active strip isn't in active_channel set to None.
if getattr(sed.active_strip, "channel", -1) != active_channel:
    sed.active_strip = None

sequences = sed.sequences_all
# select all strips in active channel
for strip in sequences:
    if strip.channel == active_channel:
        print(f'{strip.name} - {strip.frame_final_start} - {strip.frame_final_end}')