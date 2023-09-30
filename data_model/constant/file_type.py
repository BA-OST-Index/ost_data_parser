# JSON files that actually carry data
FILE_CONSTANT = 0

FILE_TRACK_OST = 1
FILE_TRACK_SHORT = 2
FILE_TRACK_ANIMATION = 3
FILE_TRACK_OTHER = 4

FILE_STORY_MAIN = 11
FILE_STORY_SIDE = 12
FILE_STORY_SHORT = 13
FILE_STORY_EVENT = 14
FILE_STORY_BOND = 15
FILE_STORY_OTHER = 16

FILE_BATTLE_MAIN = 21
FILE_BATTLE_EVENT = 22
FILE_BATTLE_ARENA = 23
FILE_BATTLE_TOTAL_ASSAULT = 24
FILE_BATTLE_BOUNTY_HUNT = 25
FILE_BATTLE_SCHOOL_EXCHANGE = 26
FILE_BATTLE_SPECIAL_COMMISSION = 27

FILE_UI_CHILD = 31
FILE_UI_EVENT = 32

FILE_VIDEO_INFO = 41

FILE_STUDENT_INFO = 51
FILE_CHARACTER_INFO = 52

FILE_TAG_INFO = 61

FILE_BACKGROUND_INFO = 71

FILE_VIRTUAL_DATA = 81

# JSON file `_all.json`, for managing different folders
FILE_DIR_ROOT = -10  # /data/all.json
FILE_DIR_TRACK_ALL = -11  # /data/track
FILE_DIR_TRACK_CATEGORY = -12  # /data/track/xxx

FILE_DIR_MAIN_ALL = -21  # /data/main/all.json
FILE_DIR_MAIN_STORY_ALL = -22  # /data/main/story/all.json
FILE_DIR_MAIN_STORY_CATEGORY = -23  # /data/main/story/xx/all.json
FILE_DIR_MAIN_STORY_VOLUME = -24  # /data/main/story/xx/yy/all.json
FILE_DIR_MAIN_STORY_CHAPTER = -25  # /data/main/story/xx/yy/zz/all.json
FILE_DIR_MAIN_BATTLE_ALL = -26  # /data/main/battle/all.json
FILE_DIR_MAIN_BATTLE_CATEGORY = -27  # /data/main/battle/xx/all.json
FILE_DIR_MAIN_BATTLE_CHAPTER = -28  # /data/main/battle/xx/yy/all.json
FILE_DIR_MAIN_BATTLE_ARENA = -29  # Special case: /data/main/battle/arena/all.json
FILE_DIR_MAIN_BATTLE_3 = -30  # Reserved: /data/main/battle/xx/yy/zz/all.json
# -31 ~ -39 are reserved.

FILE_DIR_EVENT_ALL = -41  # /data/event/all.json
FILE_DIR_EVENT_CATEGORY = -42  # /data/event/xx/all.json
FILE_DIR_EVENT_STORY = -43  # /data/event/xx/story/all.json
FILE_DIR_EVENT_BATTLE = -44  # /data/event/xx/battle/all.json
FILE_DIR_EVENT_UI = -45  # /data/event/xx/ui/all.json

FILE_DIR_CHARACTER_ALL = -51  # /data/character/all.json
FILE_DIR_CHARACTER_CATEGORY = -52  # /data/character/xx/all.json
FILE_DIR_STUDENT_SINGLE = -53  # /data/character/student/xx/all.json
FILE_DIR_STUDENT_BOND = -54  # /data/character/student/xx/bond/all.json

FILE_DIR_UI_ALL = -61  # /data/ui/all.json
FILE_DIR_UI_CATEGORY = -62  # /data/ui/xx/all.json

FILE_DIR_VIDEO_ALL = -71  # /data/video/all.json

# Reserved for future usage.
# It is now hard-coded in `data_model.config` file.
FILE_DIR_I18N_ALL = -81  # /data/i18n/all.json
FILE_DIR_I18N_CATEGORY = -82  # /data/i18n/xx/all.json

FILE_DIR_TAG_ALL = -91  # /data/tag/all.json

FILE_DIR_BACKGROUND_ALL = -101  # /data/background/all.json

# /////////////////////////////////////////////////////////////////
# Filetypes set
FILETYPES_TRACK = [FILE_TRACK_OST, FILE_TRACK_SHORT, FILE_TRACK_OTHER, FILE_TRACK_ANIMATION]
FILETYPES_STORY = [FILE_STORY_MAIN, FILE_STORY_SIDE, FILE_STORY_SHORT, FILE_STORY_BOND, FILE_STORY_OTHER]
FILETYPES_BATTLE = [FILE_BATTLE_MAIN, FILE_BATTLE_ARENA, FILE_BATTLE_TOTAL_ASSAULT, FILE_BATTLE_BOUNTY_HUNT,
                    FILE_BATTLE_SCHOOL_EXCHANGE, FILE_BATTLE_SPECIAL_COMMISSION]
FILETYPES_BACKGROUND = [FILE_BACKGROUND_INFO]
FILETYPES_CHARACTER = [FILE_STUDENT_INFO, FILE_CHARACTER_INFO]

FILETYPES_TRACK_DIR = [FILE_DIR_TRACK_ALL, FILE_DIR_TRACK_CATEGORY]
FILETYPES_STORY_DIR = [FILE_DIR_MAIN_STORY_ALL, FILE_DIR_MAIN_STORY_CATEGORY, FILE_DIR_MAIN_STORY_VOLUME,
                       FILE_DIR_MAIN_STORY_CHAPTER, FILE_DIR_STUDENT_BOND]
FILETYPES_BATTLE_DIR = [FILE_DIR_MAIN_BATTLE_ALL, FILE_DIR_MAIN_BATTLE_CATEGORY, FILE_DIR_MAIN_BATTLE_CHAPTER,
                        FILE_DIR_MAIN_BATTLE_ARENA, FILE_DIR_MAIN_BATTLE_3]
FILETYPES_UI_DIR = [FILE_DIR_UI_ALL, FILE_DIR_UI_CATEGORY]
FILETYPES_EVENT_DIR = [FILE_DIR_EVENT_STORY, FILE_DIR_EVENT_UI, FILE_DIR_EVENT_ALL, FILE_DIR_EVENT_CATEGORY,
                       FILE_DIR_EVENT_BATTLE]

