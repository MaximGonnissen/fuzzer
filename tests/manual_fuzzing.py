import json
import os

from src.fuzzer.fuzzer import Fuzzer

maps_directory = "./tests/test_maps/"

sequences = [
    "Q",
    "SQ",
    "E"
    " ",
    "",
    "\n",
    "SE"
]


def run_all() -> None:
    """
    Performs fuzzing for combinations of all test maps & sequences.
    """
    config = json.load(open("./data/config/config.json", "r"))

    config["seed"] = "test"

    fuzzer = Fuzzer(config=config)

    maps = os.listdir(maps_directory)

    for input_map in maps:
        for sequence in sequences:
            map_string = open(maps_directory + input_map, "r").read()
            fuzzer.run_jpacman(map_string, sequence, f"input_map: {input_map}")

    fuzzer.generate_report(name="manual_fuzzing")


def run_single(map_name: str, sequence: str) -> None:
    """
    Performs fuzzing for a single map & sequence.
    :param map_name: Input map name.
    :param sequence: Input sequence.
    """
    config = json.load(open("./data/config/config.json", "r"))

    config["seed"] = "test"

    fuzzer = Fuzzer(config=config)

    try:
        map_string = open(maps_directory + map_name, "r").read()
    except FileNotFoundError:
        print("Map not found.")
        return

    fuzzer.run_jpacman(map_string, sequence, f"input_map: {map_name}")

    fuzzer.generate_report(name="manual_fuzzing")


if __name__ == '__main__':
    # run_all()
    run_single("test_order.map", "SE")
