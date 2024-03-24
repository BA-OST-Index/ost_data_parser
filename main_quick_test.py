import time

from data_model.loader.loader_detect import get_loader_by_filepath
from data_model.actual_data.virtual_loader import *
from data_model.tool.tool import PostExecutionManager

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
ALBUMS = get_loader_by_filepath([], r"data/album", None)
FolderLoaderAccesser(TAGS, TRACKS, BACKGROUNDS, CHARACTERS, STORIES, BATTLES, UIS, VIDEOS, EVENTS, ALBUMS)
PostExecutionManager.execute_pool("related_to")
PostExecutionManager.execute_pool("reference_data")
PostExecutionManager.execute_pool("background_character_direct")
print(f"Linking Stuff Together: {time.time() - start_time:0.2f}")