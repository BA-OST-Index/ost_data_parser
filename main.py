import json
import pprint

from data_model.loader.track import TrackInfo

with open("data/track/ost/1.json", mode="r", encoding="UTF-8") as file:
    data = json.load(file)

print(json.dumps(TrackInfo(data).to_json(), ensure_ascii=False, indent=4))
