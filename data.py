import configparser
import csv
import os

from abc import abstractmethod, ABC
from io import StringIO


class DataLoader(ABC):
    CONFIG_FILENAME = 'config.ini'
    CSV_FILENAME = 'replies.csv'

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.status = self.config.read(self.CONFIG_FILENAME)
        if not self.status:
            self.config['secret'] = {'token': ''}
            self.config['csv'] = {'filename': self.CSV_FILENAME}
            with open(self.CONFIG_FILENAME, 'w') as configfile:
                self.config.write(configfile)

    def _truncate(self, value, limit = 15):
        shorten = (value[:limit] + '..') if len(value) > limit + 2 else value
        return shorten.ljust(limit + 2)

    def get_token(self):
        return self.config['secret']['token']

    @abstractmethod
    def add(self, row):
        pass

    @abstractmethod
    def delete(self, index):
        pass

    @abstractmethod
    def list(self, truncate = False):
        pass


class CsvLoader(DataLoader):
    TEMPORARY_FILENAME = 'temporary_operation.csv'

    def __init__(self):
        super().__init__()
        self.hostname = self.config.get(
                'csv', 'filename', fallback = self.CSV_FILENAME)

    def add(self, row):
        success = False
        entry = list(csv.reader(StringIO(row), delimiter=','))[0]
        if len(entry) == 4 and entry[2].isdigit():
            with open(self.hostname, 'a', newline='', encoding='utf8') as file:
                csv.writer(file).writerow(entry)
                success = True
        return success

    def delete(self, index):
        found = False
        with open(self.hostname, 'r', newline='', encoding='utf8') as source, \
                open(self.TEMPORARY_FILENAME, 'w',
                newline='', encoding='utf8') as target:
            writer = csv.writer(target)
            for idx, row in enumerate(csv.reader(source)):
                if idx != index:
                    writer.writerow(row)
                else:
                    found = True
        if found:
            os.remove(self.hostname)
            os.rename(self.TEMPORARY_FILENAME, self.hostname)
        else:
            os.remove(self.TEMPORARY_FILENAME)
        return found

    def list(self, truncate = False, index = -1):
        with open(self.hostname, newline='', encoding='utf8') as ideas:
            reader = csv.reader(ideas)
            result = []
            modification = self._truncate if truncate else lambda x, y: x
            for iteration, row in enumerate(reader):
                current = list(map(modification, row, [8, 12, 1, 1]))
                if index < 0 or iteration == index:
                    result.append(current)
            return result
