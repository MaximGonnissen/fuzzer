import string
from abc import ABC, abstractmethod
from logging import Logger
from random import Random

from .enums import MapItem


class BaseMapStringGenerator(ABC):
    """
    Base class for map string generators.
    """

    def __init__(self, random: Random, config: dict, logger: Logger, *args, **kwargs) -> None:
        self.random = random
        self.config = config
        self.logger = logger
        self.map_string = ""

    def __call__(self, *args, **kwargs) -> str:
        """
        Generate a new map string, calling the generate method.
        :return: The generated map string.
        """
        return self.generate(*args, **kwargs)

    def generate(self, *args, **kwargs) -> str:
        """
        Generate a new map string.
        """
        self._pre_generate(*args, **kwargs)
        self._generate(*args, **kwargs)
        self._post_generate(*args, **kwargs)
        return self.map_string

    @abstractmethod
    def _generate(self, *args, **kwargs) -> None:
        """
        Generate a new map string.
        """
        raise NotImplementedError()

    @abstractmethod
    def _pre_generate(self, *args, **kwargs) -> None:
        """
        Do any pre-generation setup.
        """
        raise NotImplementedError()

    @abstractmethod
    def _post_generate(self, *args, **kwargs) -> None:
        """
        Do any post-generation cleanup.
        """
        raise NotImplementedError()

    @abstractmethod
    def _generate_char(self, *args, **kwargs) -> str:
        """
        Generate the next character in the map string.
        """
        raise NotImplementedError()


class C0MapStringGenerator(BaseMapStringGenerator):
    """
    Generator for map strings with correctness 0.

    Random binary string map.
    """

    def _generate(self, *args, **kwargs) -> None:
        max_map_size = self.config.get("max_map_size")
        max_width = max_map_size[0]
        max_height = max_map_size[1]

        actual_width = self.random.randint(1, max_width)
        actual_height = self.random.randint(1, max_height)

        for y in range(actual_height):
            for x in range(actual_width):
                self.map_string += self._generate_char()
            self.map_string += "\n"

    def _pre_generate(self, *args, **kwargs) -> None:
        self.map_string = ""

    def _post_generate(self, *args, **kwargs) -> None:
        pass

    def _generate_char(self, *args, **kwargs) -> str:
        return str(self.random.randint(0, 1))


class C1MapStringGenerator(C0MapStringGenerator):
    """
    Generator for map strings with correctness 1.

    Random alphabetical string map.
    """

    def _generate_char(self, *args, **kwargs) -> str:
        return self.random.choice(string.ascii_letters)


class C2MapStringGenerator(C0MapStringGenerator):
    """
    Generator for map strings with correctness 2.

    Random choice of valid map characters.
    """

    def _generate_char(self, *args, **kwargs) -> str:
        return self.random.choice(list(MapItem)).value


class C3MapStringGenerator(C2MapStringGenerator):
    """
    Generator for map strings with correctness 3.

    Correctness 2 + valid number of players (1).
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.player_generated = False

    def _pre_generate(self, *args, **kwargs) -> None:
        super()._pre_generate(*args, **kwargs)
        self.player_generated = False

    def _generate_char(self, *args, **kwargs) -> str:
        if not self.player_generated:
            map_item = super()._generate_char(*args, **kwargs)
            if map_item == MapItem.PLAYER.value:
                self.player_generated = True
            return map_item
        else:
            valid_map_items = list(MapItem)
            valid_map_items.remove(MapItem.PLAYER)
            return self.random.choice(valid_map_items).value


map_string_generators = {0: C0MapStringGenerator,
                         1: C1MapStringGenerator,
                         2: C2MapStringGenerator,
                         3: C3MapStringGenerator}
