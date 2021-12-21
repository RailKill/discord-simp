import configparser
import csv
import os

from abc import abstractmethod, ABC
from discord import Permissions
from io import StringIO


class DataLoader(ABC):
    CONFIG_FILENAME = 'config.ini'
    CSV_FILENAME = 'replies.csv'
    LOCKS_FILENAME = 'locks.csv'
    NUMBER_OF_COMMANDS = 5

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.status = self.config.read(self.CONFIG_FILENAME)
        if not self.status:
            self.config['secret'] = {'token': ''}
            self.config['csv'] = {
                'filename': self.CSV_FILENAME,
                'locks': self.LOCKS_FILENAME,
            }
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
    DELETING_FILENAME = 'deleting.csv'

    def __init__(self):
        super().__init__()
        self.hostname = self.config.get(
                'csv', 'filename', fallback = self.CSV_FILENAME)
        self.lockname = self.config.get(
                'csv', 'locks', fallback = self.LOCKS_FILENAME)

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
                open(self.DELETING_FILENAME, 'w',
                newline='', encoding='utf8') as target:
            writer = csv.writer(target)
            for idx, row in enumerate(csv.reader(source)):
                if idx != index:
                    writer.writerow(row)
                else:
                    found = True
        if found:
            os.remove(self.hostname)
            os.rename(self.DELETING_FILENAME, self.hostname)
        else:
            os.remove(self.DELETING_FILENAME)
        return found

    def get_locks(self):
        with open(self.lockname, 'r', newline='', encoding='utf8') as locks:
            results = []
            for row in csv.reader(locks):
                lock = [value.split(',') for value in row]
                results.append(CommandLock(*lock))
            while len(results) < self.NUMBER_OF_COMMANDS:
                results.append(CommandLock())
            return results

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

    def set_locks(self, row, reset = False):
        updated = False
        if row:
            data = list(csv.reader(StringIO(row), delimiter=','))[0] if \
                    not reset else ['administrator', '', '']
            if len(data) == 3:
                is_num_role = not data[1] or data[1].replace(',', '').isdigit()
                is_num_user = not data[2] or data[2].replace(',', '').isdigit()
                if is_num_role and is_num_user:
                    with open(self.lockname, 'w+',
                            newline='', encoding='utf8') as out:
                        writer = csv.writer(out)
                        for i in range(self.NUMBER_OF_COMMANDS):
                            writer.writerow(data)
                        updated = True
        return updated


class CommandLock:
    def __init__(self, permissions = ['administrator'],
                roles = [], users = []):
        self.permissions = self._set_permissions(permissions)
        self.roles = self._convert_to_integer(roles)
        self.users = self._convert_to_integer(users)

    def __iter__(self):
        for values in [self.permissions, self.roles, self.users]:
            yield values

    def _convert_to_integer(self, values):
        result = []
        for value in values:
            try:
                result.append(int(value))
            except ValueError:
                pass
        return result

    def _set_permissions(self, attribute_list):
        permissions = Permissions()
        filtered_list = filter(
                lambda x: hasattr(permissions, x), attribute_list)
        for attribute in filtered_list:
            setattr(permissions, attribute, True)
        return permissions
