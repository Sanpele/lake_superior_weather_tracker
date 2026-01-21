import logging
from abc import ABC


class GenericParser(ABC):

    logger = logging.getLogger(__name__)

    def parse(self, raw_data: dict):
        pass
