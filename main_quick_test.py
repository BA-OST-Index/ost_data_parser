import time
import os
import json
from functools import partial

from data_model.loader.loader_detect import get_loader_by_filepath
from data_model.actual_data.virtual_loader import *
from data_model.tool.tool import PostExecutionManager

start_time = time.time()
TAGS = get_loader_by_filepath([], r"data/tag", None)
COMPOSERS = get_loader_by_filepath([], r"data/composer", None)
TRACKS = get_loader_by_filepath([], r"data/track", None)
BACKGROUNDS = get_loader_by_filepath([], r"data/background", None)
CHARACTERS = get_loader_by_filepath([], r"data/character", None)
STORIES = get_loader_by_filepath(["main"], r"data/main/story", None)
BATTLES = get_loader_by_filepath(["main"], r"data/main/battle", None)
UIS = get_loader_by_filepath([], r"data/ui", None)
VIDEOS = get_loader_by_filepath([], r"data/video", None)
EVENTS = get_loader_by_filepath([], r"data/event", None)
ALBUMS = get_loader_by_filepath([], r"data/album", None)
FolderLoaderAccesser(TAGS, TRACKS, BACKGROUNDS, CHARACTERS, STORIES, BATTLES, UIS, VIDEOS, EVENTS, ALBUMS)
PostExecutionManager.execute_pool("related_to")
PostExecutionManager.execute_pool("reference_data")
PostExecutionManager.execute_pool("background_character_direct")
print(f"Linking Stuff Together: {time.time() - start_time:0.2f}")

dump_json = partial(json.dumps, ensure_ascii=False)


def write_loader(target_loader):
    """XxxInfo专用"""
    loader = target_loader.loader
    dump_json(loader.to_json())


def write_loader2(target_loader):
    """XxxLoader专用"""
    loader = target_loader
    dump_json(loader.to_json())


def write_loader3(target_loader):
    """VirtualData专用"""
    loader = target_loader
    dump_json(loader.to_json())


start_time = time.time()

# export tags
print("Exporting tag")
write_loader2(TAGS)
for i in TAGS.including:
    write_loader(i)

# export composers
print("Exporting composer")
write_loader2(COMPOSERS)
for i in COMPOSERS.including:
    write_loader(i)

# export tracks
print("Exporting track")
write_loader2(TRACKS)
for track_type in TRACKS.including:
    write_loader2(track_type.loader)
    for track in track_type.loader.including:
        write_loader(track)

# export backgrounds
print("Exporting background")
write_loader2(BACKGROUNDS)
for background in BACKGROUNDS.including:
    write_loader(background)

# export characters
print("Exporting character")
write_loader2(CHARACTERS)
for char_type in CHARACTERS.including:
    write_loader2(char_type.loader)
    for char in char_type.loader.including:
        loader = char.loader
        dump_json(loader.to_json())

        if char.loader.filetype == -53:
            for bond_dir in char.loader.including:
                for bond in bond_dir.loader.including:
                    write_loader(bond)

# export stories
print("Exporing story")
write_loader2(STORIES)
for story_type in STORIES.including:
    write_loader2(story_type.loader)
    for volume in story_type.loader.including:
        write_loader2(volume.loader)
        for chapter in volume.loader.including:
            write_loader2(chapter.loader)
            for segment in chapter.loader.including:
                write_loader(segment)

# export battle
print("Exporting battle")
write_loader2(BATTLES)
for battle_type in BATTLES.including:
    write_loader2(battle_type.loader)
    # for main
    if battle_type.loader.namespace[-1] == "main":
        for chapter in battle_type.loader.including:
            write_loader2(chapter.loader)
            for segment in chapter.loader.including:
                write_loader(segment)
    else:
        for segment in battle_type.loader.including:
            write_loader(segment)

# export ui
print("Exporting UI")
write_loader2(UIS)
for ui in UIS.including:
    write_loader(ui)

# export videos
print("Exporting video")
write_loader2(VIDEOS)
for video in VIDEOS.including:
    write_loader(video)

# export events
print("Exporting event")
write_loader2(EVENTS)
for event_id in EVENTS.including:
    write_loader2(event_id.loader)
    for folder in event_id.loader.including:
        write_loader2(folder.loader)
        for file in folder.loader.including:
            write_loader(file)

# export albums
print("Exporting album")
write_loader2(ALBUMS)
for album in ALBUMS.including:
    write_loader(album)

print(f"Exporting test complate: {time.time() - start_time:0.2f}")
