import json

from src.fuzzer.fuzzer import Fuzzer

maps_directory = "./tests/test_maps/"

cases = [
    ["test1.map", "Q"]
]

if __name__ == '__main__':
    config = json.load(open("./data/config/config.json", "r"))

    config["seed"] = "test"

    fuzzer = Fuzzer(config=config)

    for case in cases:
        fuzzer.run_jpacman(maps_directory + case[0], case[1])

    fuzzer.generate_report()
