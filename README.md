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

```json
{
  "log_path": "./data/logs/",
  --
  Path
  to
  store
  logs
  "output_path": "./data/output/",
  --
  Path
  to
  store
  output
  (e.g.
  generated
  maps
  and
  the
  report)
  "jpacman_path": "./jpacman/jpacman-3.0.1.jar",
  --
  Path
  to
  JPacman
  executable
  "seed": null,
  --
  Seed
  for
  the
  random
  generator,
  null
  for
  random
  seed
  "verbose": false,
  --
  Whether
  to
  print
  verbose
  output
  "max_map_size": [
    --
    Maximum
    map
    size
    as
    [
      width,
      height
    ]
    20,
    20
  ],
  "max_action_sequence_length": 20,
  --
  Maximum
  length
  of
  the
  action
  sequence
  "jpacman_timeout": 10,
  --
  Timeout
  for
  JPacman
  in
  seconds
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
