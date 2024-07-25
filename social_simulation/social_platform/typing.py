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


class RecsysType(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    RANDOM = "random"
