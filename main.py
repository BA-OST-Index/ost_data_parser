import os
import json
import time
from functools import partial

from data_model.loader.loader_detect import get_loader_by_filepath

start_time = time.time()
TAGS = get_loader_by_filepath([], r"data/tag", None)
TRACKS = get_loader_by_filepath([], r"data/track", None)
BACKGROUNDS = get_loader_by_filepath([], r"data/background", None)
CHARACTERS = get_loader_by_filepath([], r"data/character", None)
STORIES = get_loader_by_filepath(["main"], r"data/main/story", None)
BATTLES = get_loader_by_filepath(["main"], r"data/main/battle", None)
UIS = get_loader_by_filepath([], r"data/ui", None)
VIDEOS = get_loader_by_filepath([], r"data/video", None)
EVENTS = get_loader_by_filepath([], r"data/event", None)
print(f"Linking Stuff Together: {time.time() - start_time:0.2f}")

BASE_EXPORT = "data_export/"

join_base = partial(os.path.join, BASE_EXPORT)
dump_json = partial(json.dump, ensure_ascii=False)


def create_export_dir(loader):
    joined = join_base(loader.get_path(filename=True))
    splited = os.path.split(joined)
    os.makedirs(splited[0], exist_ok=True)


def write_loader(target_loader):
    loader = target_loader.loader
    path = loader.get_path(filename=True)
    create_export_dir(loader)
    with open(join_base(path), mode="w", encoding="UTF-8") as file:
        dump_json(loader.to_json(), file)

def write_loader2(target_loader):
    loader = target_loader
    path = loader.get_path(filename=False)
    os.makedirs(join_base(path), exist_ok=True)
    with open(join_base(path, "_all.json"), mode="w", encoding="UTF-8") as file:
        dump_json(loader.to_json(), file)


start_time = time.time()
# export tags
write_loader2(TAGS)
for i in TAGS.including:
    write_loader(i)

# export tracks
write_loader2(TRACKS)
for track_type in TRACKS.including:
    write_loader2(track_type.loader)
    for track in track_type.loader.including:
        write_loader(track)

# export backgrounds
write_loader2(BACKGROUNDS)
for background in BACKGROUNDS.including:
    write_loader(background)

# export characters
write_loader2(CHARACTERS)
for char_type in CHARACTERS.including:
    write_loader2(char_type.loader)
    for char in char_type.loader.including:
        loader = char.loader
        path = loader.get_path(filename=False)
        os.makedirs(join_base(path), exist_ok=True)

        splited = path.split("/")
        path = "/".join([*splited, splited[-1] + ".json"])

        with open(join_base(path), mode="w", encoding="UTF-8") as file:
            dump_json(loader.to_json(), file)

        if char.loader.filetype == -53:
            for bond_dir in char.loader.including:
                for bond in bond_dir.loader.including:
                    write_loader(bond)

# export stories
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
write_loader2(UIS)
for ui in UIS.including:
    write_loader(ui)

# export videos
write_loader2(VIDEOS)
for video in VIDEOS.including:
    write_loader(video)

# export events
write_loader2(EVENTS)
for event_id in EVENTS.including:
    write_loader2(event_id.loader)
    for folder in event_id.loader.including:
        write_loader2(folder.loader)
        for file in folder.loader.including:
            write_loader(file)
print(f"Writing stuff: {time.time() - start_time:0.2f}")
