import os
import json
from functools import partial

from data_model.loader.loader_detect import get_loader_by_filepath

TAGS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\tag", None)
TRACKS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\track", None)
BACKGROUNDS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\background", None)
CHARACTERS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\character", None)
STORIES = get_loader_by_filepath(["main"], r"F:\GitFile\BA_OST_Index_Parser\data\main\story", None)
BATTLES = get_loader_by_filepath(["main"], r"F:\GitFile\BA_OST_Index_Parser\data\main\battle", None)
UIS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\ui", None)
VIDEOS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\video", None)
EVENTS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\event", None)

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


# export tags
for i in TAGS.including:
    write_loader(i)

# export tracks
for track_type in TRACKS.including:
    for track in track_type.loader.including:
        write_loader(track)

# export backgrounds
for background in BACKGROUNDS.including:
    write_loader(background)

# export characters
for char_type in CHARACTERS.including:
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
for story_type in STORIES.including:
    for volume in story_type.loader.including:
        for chapter in volume.loader.including:
            for segment in chapter.loader.including:
                write_loader(segment)

# export battle
for battle_type in BATTLES.including:
    # for main
    if battle_type.loader.namespace == "main":
        for chapter in battle_type.loader.including:
            for segment in chapter.loader.including:
                write_loader(segment)
    else:
        for segment in battle_type.loader.including:
            write_loader(segment)

# export ui
for ui in UIS.including:
    write_loader(ui)

# export videos
for video in VIDEOS.including:
    write_loader(video)

# export events
for event_id in EVENTS.including:
    for folder in event_id.loader.including:
        for file in folder.loader.including:
            write_loader(file)
