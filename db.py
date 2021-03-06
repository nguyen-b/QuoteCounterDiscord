from collections import defaultdict
import json
import os

DEFAULT = "database.json"


class AppDatabase:
    def __init__(self, file=DEFAULT):
        self.file = file
        self.data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        data_file = self.load_db(self.file)
        if data_file:
            nd = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
            for year, months in data_file.items():
                for month, names in months.items():
                    for name, ct in names.items():
                        nd[year][month][name] = ct
            self.data = nd

    def add_quote(self, name, month, year):
        self.adjust_quote(name, month, year, 1)

    def adjust_quote(self, name, month, year, amount):
        year = str(int(year))
        month = str(int(month))
        name = str(name)
        self.data[year][month][name] += amount
        self.save_db()

    def clear(self, month, year):
        year = str(int(year))
        month = str(int(month))
        if month in self.data[year]:
            del self.data[year][month]
        self.save_db()

    def get_counts(self, month, year):
        month = str(int(month))
        year = str(int(year))
        if year in self.data and month in self.data[year]:
            return self.data[year][month]

    @staticmethod
    def load_db(file=DEFAULT):
        if os.path.exists(file):
            with open(file, 'r') as f:
                if os.stat(file).st_size > 0:
                    return json.load(f)

        else:
            with open(file, 'w+') as f:
                pass

    def remove_quote(self, name, month, year):
        self.adjust_quote(name, month, year, -1)

    def save_db(self):
        with open(self.file, 'w') as f:
            f.write(json.dumps(self.data, indent=4, sort_keys=True))
