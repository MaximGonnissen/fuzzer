import json
import logging
import os
import subprocess
from random import Random
from time import time

from .enums import Action, MapItem


class Fuzzer:
    """
    Fuzzer class

    1. Generates an input file and random action sequence.
    2. Runs JPacman with the generated inputs.
    3. Checks the exit code of JPacman.
    4. Generates a report of the run(s).
    """

    def __init__(self, config: dict, logger: logging.Logger = None, random: Random = None, max_iterations: int = None,
                 max_time: int = None):
        """
        Initializes the fuzzer.
        :param config: Configuration dictionary.
        :param logger: Logger to use. If None, a new logger will be created.
        :param random: Random object to use. If None, a new random object will be created.
        """
        self.config: dict = config
        self.logger: logging.Logger = logger
        self.random: Random = random
        self.verbose: bool = False

        self.history: list = []

        self.iteration: int = 0
        self.start_time: float = time()
        self.max_iterations: int = max_iterations or -1
        self.max_time: int = max_time or -1

        if not self.logger:
            self.__init_logger()

        if not self.random:
            self.__init_random()

        self.logger.debug("Fuzzer initialized")

    def __init_logger(self) -> None:
        """
        Initializes the logger with a stream handler and a file handler.
        """
        self.logger = logging.getLogger("Fuzzer")
        self.logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(stream_handler)

        log_path = self.config.get("log_path")
        if not os.path.exists(os.path.dirname(log_path)):
            try:
                os.makedirs(os.path.dirname(log_path))
                self.__verbose_log(f"Log directory created: {os.path.dirname(log_path)}")
            except OSError as e:
                self.logger.error("Could not create log directory: {}".format(e))
                raise e

        open(f"{log_path}/fuzzer.log", "w").write("")

        file_handler = logging.FileHandler(f"{log_path}/fuzzer.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(file_handler)

        self.verbose = self.config.get("verbose") or False

        self.logger.debug("Logger initialized")

    def __init_random(self) -> None:
        """
        Initializes the random object.
        """
        self.random = Random(self.config.get("seed") or None)

        self.logger.debug(f"Random object initialized.")

    def __verbose_log(self, message: str) -> None:
        """
        Logs a message if verbose is True.
        :param message: Message to log.
        """
        if self.verbose:
            self.logger.debug(message)

    def runtime(self) -> float:
        """
        Calculates the runtime of the fuzzer.
        :return: Runtime in seconds.
        """
        return time() - self.start_time

    def limit_reached(self) -> bool:
        """
        Checks if the fuzzer has reached its limit, based on the maximum iterations and maximum time.
        :return: True if the fuzzer has reached its limit, False otherwise.
        """
        return (0 <= self.max_iterations <= self.iteration) or (0 <= self.max_time <= self.runtime())

    def generate_input(self, map_string: str = None) -> None:
        """
        Generates a map input file and outputs it into the output directory under the name input.map.
        """
        output_path = self.config.get("output_path")

        if not output_path:
            self.logger.warning("No output path specified, using default output path")
            output_path = "./data/output"
            self.config["output_path"] = output_path

        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
                self.__verbose_log(f"Output directory created: {output_path}")
            except OSError as e:
                self.logger.error("Could not create output directory: {}".format(e))
                raise e

        input_file = open(os.path.join(output_path, "input.map"), "w")
        input_file.write(map_string or self.generate_map_string())

        self.__verbose_log(f"Input file generated: {input_file.name}")

    def generate_map_string(self) -> str:
        """
        Generates a map string.
        :return: Map string in a JPacman compatible format.
        """
        max_map_size = self.config.get("max_map_size")
        max_width = max_map_size[0]
        max_height = max_map_size[1]

        actual_width = self.random.randint(1, max_width)
        actual_height = self.random.randint(1, max_height)

        map_string = ""

        for y in range(actual_height):
            for x in range(actual_width):
                map_string += self.__random_map_item().value
            map_string += "\n"

        self.__verbose_log(f"Map string generated with size {actual_width}x{actual_height}:\n{map_string}")

        return map_string

    def __random_map_item(self) -> MapItem:
        """
        Generates a random map item.
        :return: Random map item.
        """
        return self.random.choice(list(MapItem))

    def generate_action_sequence(self) -> str:
        """
        Generates an action sequence.
        :return: Action sequence in a JPacman compatible format.
        """
        action_sequence = ""
        max_action_sequence_length = self.config.get("max_action_sequence_length")

        actual_action_sequence_length = self.random.randint(1, max_action_sequence_length)

        for i in range(actual_action_sequence_length):
            action_sequence += self.__random_action().value

        self.__verbose_log(f"Action sequence generated: {action_sequence}")

        return action_sequence

    def __random_action(self) -> Action:
        """
        Generates a random action.
        :return: Random action.
        """
        return self.random.choice(list(Action))

    def run_jpacman(self) -> int:
        """
        Runs JPacman with the generated input.
        :return: Exit code of JPacman.
        """
        map_string = self.generate_map_string()
        action_sequence = self.generate_action_sequence()

        self.generate_input(map_string)

        jpacman_path = self.config.get("jpacman_path")
        if not jpacman_path:
            self.logger.warning("No JPacman path specified, using default JPacman path")
            jpacman_path = "./jpacman/jpacman-3.0.1.jar"
            self.config["jpacman_path"] = jpacman_path

        jpacman_command = f"java -jar {jpacman_path} {self.config.get('output_path')}/input.map {action_sequence}"

        self.__verbose_log(f"JPacman command: {jpacman_command}")

        jpacman_process = subprocess.Popen(jpacman_command, shell=True)
        jpacman_process.wait()

        self.__verbose_log(f"JPacman exit code: {jpacman_process.returncode}")

        self.history.append([self.iteration, jpacman_process.returncode, map_string, action_sequence])

        return jpacman_process.returncode

    def run(self, report: bool = True, clear_history: bool = True) -> None:
        """
        Runs the fuzzer based on the configuration.
        :param report: Whether to generate a report.
        :param clear_history: Whether to clear the history before running.
        """
        if clear_history:
            self.history.clear()

        self.start_time = time()

        while not self.limit_reached():
            self.iteration += 1
            self.run_jpacman()

        self.logger.info(f"Fuzzer finished after {self.runtime()} seconds")

        if report:
            self.__generate_report()

    def __generate_report(self) -> None:
        """
        Generates a report.
        """
        report_start_time = time()

        output_path = self.config.get("output_path")

        statistics = {
            "iterations": self.iteration,
            "exit codes": {}
        }

        exit_codes = [history_item[1] for history_item in self.history]

        for exit_code in set(exit_codes):
            statistics["exit codes"][exit_code] = exit_codes.count(exit_code)

        with open(os.path.join(output_path, "report.md"), "w") as report_file:
            report_file.write(f"# JPacman Fuzzer Report\n\n")
            report_file.write(f"## Configuration\n\n")
            report_file.write(f"```json\n{json.dumps(self.config, indent=4)}\n```\n\n")
            report_file.write(f"## Arguments\n\n")
            report_file.write(f"```bash\n--max_iterations: {self.max_iterations}\n")
            report_file.write(f"--max_time: {self.max_time}\n```\n\n")
            report_file.write(f"## Statistics\n\n")
            report_file.write(f"```json\n{json.dumps(statistics, indent=4)}\n```\n\n")
            report_file.write(f"## History\n\n")
            report_file.write(f"| Iteration | Exit Code | Map String | Action Sequence |\n")
            report_file.write(f"| --------- | --------- | ---------- | --------------- |\n")

            for entry in self.history:
                map_string = "`" + entry[2].replace('\n', '`<br>`')[:-1]
                report_file.write(f"| {entry[0]} | {entry[1]} | {map_string} | {entry[3]} |\n")

        self.logger.info(f"Report generated in {time() - report_start_time} seconds")
        self.logger.info(f"Report generated at {os.path.join(output_path, 'report.md')}")

