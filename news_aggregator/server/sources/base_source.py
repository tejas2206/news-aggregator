from abc import ABC, abstractmethod
import logging


class NewsSource(ABC):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch_articles(self):
        pass
