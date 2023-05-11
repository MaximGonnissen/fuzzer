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

if __name__ == '__main__':
    config = json.load(open("./data/config/config.json", "r"))

    config["seed"] = "test"

    fuzzer = Fuzzer(config=config)

    maps = os.listdir(maps_directory)

    for input_map in maps:
        for sequence in sequences:
            map_string = open(maps_directory + input_map, "r").read()
            fuzzer.run_jpacman(map_string, sequence, f"input_map: {input_map}")

    fuzzer.generate_report()
