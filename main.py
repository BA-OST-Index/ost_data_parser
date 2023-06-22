import json
import pprint

from data_model.loader.track import TrackFolder
from data_model.actual_data.story import StoryInfo

t = TrackFolder(['track', 'ost'], 'data/track/ost/')

with open("data/main/story/main/1/1/1.json", mode="r", encoding="UTF-8") as file:
    content = json.load(file)

story = StoryInfo(content)
pprint.pp(story.to_json_basic())

