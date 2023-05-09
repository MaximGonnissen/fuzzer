# Fuzzer
*For assignment 8 of Software Testing // UAntwerpen // 2022-2023*
___

## Introduction

This is a simple fuzzing tool written specifically for the provided JPacman archive for assignment 8 of the Software
Testing course at the University of Antwerp.

## Requirements

- Python 3.11.0
- JPacman (Provided in `jpacman` directory)
- Compatible Java version (Tested with Java `"17.0.1" 2021-10-19 LTS`)

## Config

The default configuration can be found in `data/config/config.json`.

Example with information:

```yaml
{
  "log_path": "./data/logs/",                         # Path to store logs
  "output_path": "./data/output/",                    # Path to store output  (e.g. generated maps and the report)
  "jpacman_path": "./jpacman/jpacman-3.0.1.jar",      # Path to JPacman executable
  "seed": null,                                       # Seed for the random generator, null for random seed
  "verbose": false,                                   # Whether to print verbose output
  "max_map_size": [ # Maximum map size (as a list of [width, height])
    20,
    20
  ],
  "map_gen_format": "0",                              # Map generation format, a measure of correctness
  # 0: Random binary string map
  # 1: Random alphabetical string map
  # 2: Random choice of valid map characters
  # 3: 2 + valid number of players
  "max_action_sequence_length": 20,                   # Maximum length of the action sequence
  "jpacman_timeout": 10,                              # Timeout for JPacman in seconds
}
```

## Usage

Run from the root directory of the project with following optional arguments:

- `--config`: Path to config file (default: `data/config/config.json`)
- `--max_iterations`: Maximum number of iterations (default: `-1` (infinite))
- `--max_time`: Maximum time in seconds (default: `-1` (infinite))
- `--generate_report`: Whether to generate a report (default: `True`)

```shell
python ./src/main.py --config data/config/config.json --max_iterations 1000 --max_time 180 --generate_report True
```

## Output

The output of the fuzzer can be found in the `data/output` directory, in the `report.md` file.

Markdown was chosen as the output format because it is easy to read, well-supported, and can be converted to other
formats easily.

## Structure

Inside the fuzzer package, one can find a number of different Python files responsible for different aspects of the
fuzzer.

### fuzzer.py

The fuzzer itself, responsible for fuzzing, as well as generating the report.

### enums.py

Contains the Action & MapItem enums, which are used by the fuzzer and map string generators to provide valid inputs for
the JPacman executable.

### map_string_generator.py

Contains a variety of MapStringGenerator classes, which are used to generate random maps for the fuzzer.

A BaseMapStringGenerator class is provided, which can be extended to create new map string generators. This class is
used by various other map string generators in this file. Each generator is prefixed with C#, where the C stands for
"Correctness", and the # is the measure of correctness. The higher the number, the more correct the map string that is
generated. This corresponds with the map_gen_format in the config file.