from enum import Enum


class ActionType(Enum):
    EXIT = "exit"
    REFRESH = "refresh"
    SEARCH_USER = "search_user"
    SEARCH_POSTS = "search_posts"
    CREATE_POST = "create_post"
    LIKE = "like"
    UNLIKE = "unlike"
    DISLIKE = "dislike"
    UNDO_DISLIKE = "undo_dislike"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    MUTE = "mute"
    UNMUTE = "unmute"
    TREND = "trend"
    SIGNUP = "sign_up"
    REPOST = "repost"
    UPDATE_REC_TABLE = "update_rec_table"
    CREATE_COMMENT = "create_comment"
    LIKE_COMMENT = "like_comment"
    UNLIKE_COMMENT = "unlike_comment"
    DISLIKE_COMMENT = "dislike_comment"
    UNDO_DISLIKE_COMMENT = "undo_dislike_comment"
    DO_NOTHING = "do_nothing"


class CommunityActionType(Enum):
    EXIT = "exit"
    GO_TO = "go_to"
    STOP = "stop"
    DO_SOMETHING = "do_something"
    MEET = "meet"


class RoomName(Enum):
    ENTRANCE_BUILDING_A = "entrance(Building A)"
    KITCHEN_BUILDING_A = "kitchen(Building A)"
    DINING_ROOM_BUILDING_A = "dining room(Building A)"

    BOBS_PRIVATE_TOILET_BUILDING_A = "Bob's private toilet(Building A)"
    BOBS_PRIVATE_LIVING_ROOM_BUILDING_A = "Bob's private living room(Building A)"
    BOBS_PRIVATE_BEDROOM_BUILDING_A = "Bob's private bedroom(Building A)"
    BOBS_PRIVATE_BALCONY_BUILDING_A = "Bob's private balcony(Building A)"

    ALICES_PRIVATE_TOILET_BUILDING_A = "Alice's private toilet(Building A)"
    ALICES_PRIVATE_LIVING_ROOM_BUILDING_A = "Alice's private living room(Building A)"
    ALICES_PRIVATE_BEDROOM_BUILDING_A = "Alice's private bedroom(Building A)"
    ALICES_PRIVATE_BALCONY_BUILDING_A = "Alice's private balcony(Building A)"

    DAISYS_PRIVATE_TOILET_BUILDING_A = "Daisy's private toilet(Building A)"
    DAISYS_PRIVATE_LIVING_ROOM_BUILDING_A = "Daisy's private living room(Building A)"
    DAISYS_PRIVATE_BEDROOM_BUILDING_A = "Daisy's private bedroom(Building A)"
    DAISYS_PRIVATE_BALCONY_BUILDING_A = "Daisy's private balcony(Building A)"

    LISAS_PRIVATE_TOILET_BUILDING_A = "Lisa's private toilet(Building A)"
    LISAS_PRIVATE_LIVING_ROOM_BUILDING_A = "Lisa's private living room(Building A)"
    LISAS_PRIVATE_BEDROOM_BUILDING_A = "Lisa's private bedroom(Building A)"
    LISAS_PRIVATE_BALCONY_BUILDING_A = "Lisa's private balcony(Building A)"

    ENTRANCE_BUILDING_B = "entrance(Building B)"
    KITCHEN_BUILDING_B = "kitchen(Building B)"
    DINING_ROOM_BUILDING_B = "dining room(Building B)"

    TOMS_PRIVATE_TOILET_BUILDING_B = "Tom's private toilet(Building B)"
    TOMS_PRIVATE_LIVING_ROOM_BUILDING_B = "Tom's private living room(Building B)"
    TOMS_PRIVATE_BEDROOM_BUILDING_B = "Tom's private bedroom(Building B)"
    TOMS_PRIVATE_BALCONY_BUILDING_B = "Tom's private balcony(Building B)"

    ANDREWS_PRIVATE_TOILET_BUILDING_B = "Andrew's private toilet(Building B)"
    ANDREWS_PRIVATE_LIVING_ROOM_BUILDING_B = "Andrew's private living room(Building B)"
    ANDREWS_PRIVATE_BEDROOM_BUILDING_B = "Andrew's private bedroom(Building B)"
    ANDREWS_PRIVATE_BALCONY_BUILDING_B = "Andrew's private balcony(Building B)"

    AMYS_PRIVATE_TOILET_BUILDING_B = "Amy's private toilet(Building B)"
    AMYS_PRIVATE_LIVING_ROOM_BUILDING_B = "Amy's private living room(Building B)"
    AMYS_PRIVATE_BEDROOM_BUILDING_B = "Amy's private bedroom(Building B)"
    AMYS_PRIVATE_BALCONY_BUILDING_B = "Amy's private balcony(Building B)"

    WEST_GARDEN = "west garden"
    EAST_GARDEN = "east garden"
    SQUARE = "square"
    BASKETBALL_COURT = "basketball court"  # Note: "cert" seems to be a typo, consider "BASKETBALL_COURT" if it was meant to be "court".
    CARD_ROOM = "card room"
    NORTH_ROOM_IN_LIBRARY = "north room in library"
    SOUTH_ROOM_IN_LIBRARY = "south room in library"
    ACTIVITY_ROOM = "activity room"

    CHURCH = "church"

    OFFICE = "office"
    SCHOOL = "school"


class RecsysType(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    RANDOM = "random"
