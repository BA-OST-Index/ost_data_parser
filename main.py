from data_model.loader.loader_detect import get_loader_by_filepath

TAGS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\tag", None)
TRACKS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\track", None)
BACKGROUNDS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\background", None)
CHARACTERS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\character", None)
STORIES = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\main\story", None)
BATTLES = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\main\battle", None)
UIS = get_loader_by_filepath([], r"F:\GitFile\BA_OST_Index_Parser\data\ui", None)
