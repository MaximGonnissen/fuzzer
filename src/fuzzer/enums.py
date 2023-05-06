from enum import Enum


class MapItem(Enum):
    """
    Enum for map items
    """
    WALL = "W"
    EMPTY = "0"
    MONSTER = "M"
    PLAYER = "P"
    FOOD = "F"


class Action(Enum):
    """
    Enum for actions
    """
    EXIT = "E"
    START = "S"
    QUIT = "Q"
    SLEEP = "W"
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"
