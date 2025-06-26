from abc import ABC, abstractmethod

class NewsSource(ABC):
    @abstractmethod
    def fetch_articles(self):
        pass
