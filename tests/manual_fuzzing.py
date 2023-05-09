import json
import os

from src.fuzzer.fuzzer import Fuzzer

maps_directory = "./tests/test_maps/"

sequences = [
    "Q",
    "SQ"
]

if __name__ == '__main__':
    config = json.load(open("./data/config/config.json", "r"))

    config["seed"] = "test"

    fuzzer = Fuzzer(config=config)

    maps = os.listdir(maps_directory)

    for input_map in maps:
        for sequence in sequences:
            fuzzer.run_jpacman(maps_directory + input_map, sequence)

    fuzzer.generate_report()
