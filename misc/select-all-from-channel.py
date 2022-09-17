import bpy


# selects all elements from specific channel
def select_all_from_channel(active_channel: int):
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
        
select_all_from_channel(2)