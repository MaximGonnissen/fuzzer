import json
import logging
import os
import subprocess
from logging import Logger
from random import Random
from time import time

from .enums import Action, MapItem
from .map_string_generator import map_string_generators


class Fuzzer:
    """
    Fuzzer class

    1. Generates an input file and random action sequence.
    2. Runs JPacman with the generated inputs.
    3. Checks the exit code of JPacman.
    4. Generates a report of the run(s).
    """

    def __init__(self, config: dict, logger: Logger = None, random: Random = None, max_iterations: int = None,
                 max_time: int = None):
        """
        Initializes the fuzzer.
        :param config: Configuration dictionary.
        :param logger: Logger to use. If None, a new logger will be created.
        :param random: Random object to use. If None, a new random object will be created.
        :param max_iterations: Maximum number of iterations to run. If None, the fuzzer will run indefinitely (or until the maximum time is reached).
        :param max_time: Maximum time to run in seconds. If None, the fuzzer will run indefinitely (or until the maximum iterations are reached).
        """
        self.config: dict = config
        self.logger: Logger = logger
        self.random: Random = random
        self.verbose: bool = False

        self.history: list = []
        self.mutation_history: list = []  # Hashes of mutated maps + action sequences

        self.iteration: int = 0
        self.start_time: float = time()
        self.last_progress_report: float = time()
        self.max_iterations: int = max_iterations or -1
        self.max_time: int = max_time or -1

        if not self.logger:
            self.__init_logger()

        if not self.random:
            self.__init_random()

        self.map_string_generator = map_string_generators[self.config.get("map_gen_format")](self.random,
                                                                                             self.config,
                                                                                             self.logger)

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

    def generate_input(self, map_string: str) -> None:
        """
        Generates a map input file and outputs it into the output directory under the name input.map.
        :param map_string: Map string to use. If None, a new map string will be generated.
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
        input_file.write(map_string)

        self.__verbose_log(f"Input file generated: {input_file.name}")

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

        # Ensure action sequence ends with exit to prevent JPacman from hanging
        if self.config.get("map_gen_format") >= 3:
            action_sequence = action_sequence[:-1] + "E"

        self.__verbose_log(f"Action sequence generated: {action_sequence}")

        return action_sequence

    def __random_action(self) -> Action:
        """
        Generates a random action.
        :return: Random action.
        """
        return self.random.choice(list(Action))

    def run_jpacman(self, map_string: str = None, action_sequence: str = None, note: str = None) -> int:
        """
        Runs JPacman with the generated input.
        :param map_string: Map string to use. If None, a new map string will be generated.
        :param action_sequence: Action sequence to use. If None, a new action sequence will be generated.
        :param note: Note to add to the history entry.
        :return: Exit code of JPacman.
        """
        if map_string is None:
            map_string = self.map_string_generator()

        if action_sequence is None:
            action_sequence = self.generate_action_sequence()

        self.generate_input(map_string)

        jpacman_path = self.config.get("jpacman_path")
        if not jpacman_path:
            self.logger.warning("No JPacman path specified, using default JPacman path")
            jpacman_path = "./jpacman/jpacman-3.0.1.jar"
            self.config["jpacman_path"] = jpacman_path

        jpacman_command = f"java -jar {jpacman_path} {self.config.get('output_path')}/input.map {action_sequence}"

        self.__verbose_log(f"JPacman command: {jpacman_command}")

        try:
            jpacman_process = subprocess.run(jpacman_command, timeout=self.config.get("jpacman_timeout"), text=True,
                                             capture_output=True)
            return_code = jpacman_process.returncode
            process_output = jpacman_process.stdout + jpacman_process.stderr
        except subprocess.TimeoutExpired:
            self.logger.warning("JPacman timed out")
            return_code = "timeout"
            process_output = ""

        self.__verbose_log(f"JPacman exit code: {return_code}")

        self.iteration += 1

        self.history.append([self.iteration, return_code, map_string, action_sequence, process_output, note])

        return return_code

    def __prep_run(self, clear_history: bool) -> None:
        if clear_history:
            self.history.clear()

        self.start_time = time()
        self.last_progress_report = time()

        if self.max_time <= 0 and self.max_iterations <= 0:
            self.logger.warning("No limit specified, the fuzzer will run indefinitely!")

    def __finish_run(self, generate_report: bool) -> None:
        runtime = self.runtime()

        self.logger.info(
            f"Fuzzer finished after {runtime}(/{self.max_time}) seconds | {self.iteration}(/{self.max_iterations}) iterations")

        if generate_report:
            self.generate_report(runtime=runtime)

    def run(self, generate_report: bool = True, clear_history: bool = True, update_interval: int = 20) -> None:
        """
        Runs the fuzzer based on the configuration.
        :param generate_report: Whether to generate a report.
        :param clear_history: Whether to clear the history before running.
        :param update_interval: Interval in seconds to update the progress report.
        """

        def progress_report():
            """
            Prints the progress of the fuzzer every update_interval seconds.
            """
            nonlocal update_interval

            if update_interval == -1:
                return

            if time() - self.last_progress_report >= update_interval:
                self.last_progress_report = time()

                time_progress = None
                iteration_progress = None
                if self.max_time > 0:
                    time_progress = self.runtime() / self.max_time

                if self.max_iterations > 0:
                    iteration_progress = self.iteration / self.max_iterations

                progress_update = ""

                if time_progress is not None or iteration_progress is not None:
                    relevant_progress = max(time_progress or 0, iteration_progress or 0)
                    progress_bar = "#" * int(relevant_progress * 20)
                    progress_bar += " " * (20 - len(progress_bar))
                    progress_update = f"Progress: [{progress_bar}] {int(relevant_progress * 100)}%"

                if iteration_progress is not None:
                    progress_update += f"{' -- ' if progress_update != '' else ''} Iteration: {self.iteration}/{self.max_iterations}"

                if time_progress is not None:
                    progress_update += f"{' -- ' if progress_update != '' else ''} Time: {self.runtime()}/{self.max_time} seconds"

                progress_update += f"{' -- ' if progress_update != '' else ''}Elapsed: {self.runtime()}"

                self.logger.info(progress_update)

        self.__prep_run(clear_history=clear_history)

        while not self.limit_reached():
            self.run_jpacman()
            progress_report()

        self.__finish_run(generate_report=generate_report)

    def mutate_run(self, initial_map_string: str, initial_action_sequence: str, generate_report: bool = True,
                   clear_history: bool = True, update_interval: int = 20) -> None:
        """
        Performs a run with all possible mutations of the input map and action sequence.
        :param initial_map_string: Input map string.
        :param initial_action_sequence: Action sequence string.
        :param generate_report: Whether to generate a report.
        :param clear_history: Whether to clear the history before running.
        :param update_interval: Interval in seconds to update the progress report.
        """

        def hash_inputs(new_map_string: str, new_action_sequence: str) -> int:
            """
            Hashes the input map and action sequence.
            :return: Hash of the input map and action sequence.
            """
            return hash(new_map_string + new_action_sequence)

        def previously_mutated(hash_value: int) -> bool:
            """
            Checks if the input map and action sequence have been previously mutated.
            :return: Whether the input map and action sequence have been previously mutated.
            """
            return hash_value in self.mutation_history

        def progress_report():
            """
            Prints the progress of the fuzzer every update_interval seconds.
            """
            nonlocal update_interval
            nonlocal possible_mutations

            if update_interval == -1:
                return

            if time() - self.last_progress_report >= update_interval:
                self.last_progress_report = time()

                progress = len(self.mutation_history) / possible_mutations

                progress_bar = "#" * int(progress * 20)
                progress_bar += " " * (20 - len(progress_bar))
                progress_update = f"Progress: [{progress_bar}] {int(progress * 100)}% -- Elapsed: {self.runtime()}"

                self.logger.info(progress_update)

        def mutate(map_string: str, action_sequence: str, mutate_action: bool = False, depth: int = 0,
                   previous_iteration: int = None) -> None:
            """
            Mutates the input map and action sequence and runs JPacman -- recursively.
            :param map_string: Input map string.
            :param action_sequence: Action sequence string.
            :param mutate_action: Whether to mutate the action sequence if true, or the map if false.
            :param depth: Current depth of the recursion.
            :param previous_iteration: Previous iteration. Used for the note.
            """
            new_map_string = map_string[:]
            new_action_sequence = action_sequence[:]

            previous_iteration = previous_iteration or self.iteration
            note = ""

            for i in range(len(map_string)):
                for j in range(len(action_sequence)):
                    for map_item in MapItem:
                        if not mutate_action:
                            new_map_string = map_string[:j] + map_item.value + map_string[j + 1:]
                            note = f"From iteration {previous_iteration}: Mutated {map_item} at index {i} to {map_item.value}."
                        for action in Action:
                            if mutate_action:
                                new_action_sequence = new_action_sequence[:j] + action.value + new_action_sequence[
                                                                                               j + 1:]
                                note = f"From iteration {previous_iteration}: Mutated {action} at index {j} to {action.value}."

                            hash_value = hash_inputs(new_map_string, new_action_sequence)

                            if previously_mutated(hash_value):
                                continue

                            self.mutation_history.append(hash_value)

                            if not self.limit_reached():
                                self.run_jpacman(map_string=new_map_string, action_sequence=new_action_sequence,
                                                 note=note)
                                progress_report()
                            else:
                                return

                            previous_iteration = self.iteration

                            mutate(new_map_string, new_action_sequence, mutate_action=not mutate_action,
                                   depth=depth + 1, previous_iteration=previous_iteration)

                            if not mutate_action:
                                # No need to mutate the action sequence if we're mutating the map.
                                break
                        if mutate_action:
                            # No need to mutate the map if we're mutating the action sequence.
                            break
                    if not mutate_action:
                        # No need to iterate through the action sequence if we're mutating the map.
                        break
                if mutate_action:
                    # No need to iterate through the map if we're mutating the action sequence.
                    break

        self.__prep_run(clear_history=clear_history)

        possible_mutations = (len(initial_map_string) * len(MapItem)) * (len(initial_action_sequence) * len(Action))

        self.logger.info(
            "Progress does not take into account maximum depth of the mutation tree, and thus may be inaccurate.")

        mutate(initial_map_string, initial_action_sequence)

        self.__finish_run(generate_report=generate_report)

    def generate_report(self, runtime: float = None) -> None:
        """
        Generates a report.
        """
        report_start_time = time()

        output_path = self.config.get("output_path")

        statistics = {
            "iterations": self.iteration,
            "exit codes": {},
            "errors": {}
        }

        if runtime:
            statistics["runtime"] = runtime

        exit_codes = [history_item[1] for history_item in self.history]

        for exit_code in set(exit_codes):
            statistics["exit codes"][exit_code] = exit_codes.count(exit_code)

        errors = [history_item[4] for history_item in self.history if history_item[1] != 0]

        errors_counted = {}
        for error in set(errors):
            if len(error) > 50:
                error = error[:50] + "..."
            errors_counted[error] = errors.count(error)

        # Sort errors by count
        statistics["errors"] = {error: count for error, count in
                                sorted(errors_counted.items(), key=lambda item: item[1], reverse=True)}

        with open(os.path.join(output_path, "report.md"), "w") as report_file:
            report_file.write(f"# JPacman Fuzzer Report\n\n")

            report_file.write(f"## Table of Contents\n\n")
            report_file.write(f"* [Configuration](#configuration)\n")
            report_file.write(f"* [Arguments](#arguments)\n")
            report_file.write(f"* [Statistics](#statistics)\n")
            report_file.write(f"* [History](#history)\n")

            report_file.write(f"## Configuration\n\n")
            report_file.write(f"```json\n{json.dumps(self.config, indent=4)}\n```\n\n")
            report_file.write(f"## Arguments\n\n")
            report_file.write(f"```bash\n--max_iterations: {self.max_iterations}\n")
            report_file.write(f"--max_time: {self.max_time}\n```\n\n")
            report_file.write(f"## Statistics\n\n")
            report_file.write(f"```json\n{json.dumps(statistics, indent=4)}\n```\n\n")
            report_file.write(f"## History\n\n")
            report_file.write(f"| Iteration | Exit Code | Map String | Action Sequence | Output | Notes |\n")
            report_file.write(f"| --------- | --------- | ---------- | --------------- | ------ | ----- |\n")

            for entry in self.history:
                for i in range(len(entry)):
                    if entry[i] not in ["", None]:
                        if str(entry[i]).count("\n") > 1:
                            entry[i] = ("`" + str(entry[i]).replace('\n', '`<br>`')[:-1]).replace("``", "")
                        else:
                            entry[i] = "`" + str(entry[i]).replace('\n', "\\n") + "`"
                report_file.write(f"| {entry[0]} | {entry[1]} | {entry[2]} | {entry[3]} | {entry[4]} | {entry[5]} |\n")

            report_file.write(f"\n\n> Report generated in {time() - report_start_time} seconds.")

        self.logger.info(f"Report generated in {time() - report_start_time} seconds")
        self.logger.info(f"Report generated at {os.path.join(output_path, 'report.md')}")
