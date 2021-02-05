from collections import defaultdict
import pprint
import random

from db import AppDatabase


GREETINGS = "greetings.txt"


class QuoteBot:
    MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

    def __init__(self, database, greetings=GREETINGS):
        self.database = AppDatabase(database)
        self.greetings = []
        self.load_greetings(greetings)

    def add_quote(self, name, month, year):
        self.database.add_quote(name, month, year)

    def counts(self, month, year):
        month = str(int(month))
        year = str(int(year))
        counts = self.database.get_counts(month, year)
        res = self.random_greeting() + "\n\n"
        if counts:
            res = f"**Counts for {self.MONTHS[int(month) - 1]} {year}**"
            res += self.format_counts(counts)
        else:
            res += f"**No Data for {self.MONTHS[int(month) - 1]} {year}**"
        return res

    def dump(self):
        res = self.random_greeting() + "\n\n"
        res += "**Database Dump**\n"
        res += pprint.pformat(self.database.data, indent=4)
        return res
        
    @staticmethod
    def format_counts(counts):
        res = ""
        for name, ct in sorted(counts.items(), key=lambda i : i[1], reverse=True):
            res += "\n" + f"{name.title()}: {str(ct)}"
        return res

    @staticmethod
    def format_rank(ranks):
        res = ""
        for rank, names in ranks.items():
            for name, ct in names:
                res += "\n"
                if rank == 1:
                    res += ":first_place: "
                if rank == 2:
                    res += ":second_place: "
                if rank == 3:
                    res += ":third_place: "
                res += f"{name.title()} - {ct}"
        return res
            
    def help_text(self):
        res = self.random_greeting() + "\n\n"
        res += "`$help`: gets this help menu\n"
        res += "`$add <name>`: adds one (1) tally to <name> for current month\n"
        res += "`$remove <name>`: removes one (1) tally to <name> for current month\n"
        res += "`$counts <month> <year>`: gets counts for <month> of <year>\n"
        res += "`$tallies <month> <year>`: gets tallies and ranks for <month> and <year>\n"
        res += "`$dumps`: dumps database"
        return res

    def load_greetings(self, file=GREETINGS):
        with open(file, 'r') as f:
            for line in f:
                self.greetings.append(line.rstrip())

    def monthly_tally(self, month, year):
        res = self.random_greeting() + "\n\n"
        ct = self.database.get_counts(month, year)
        if ct:
            res += f"Tallies for **{self.MONTHS[int(month) - 1]} {year}**"
            res += self.format_rank(self.rank(ct))
        else:
            res += f"No Data for **{self.MONTHS[int(month) - 1]} {year}**"

        res += "\n\n"
        year_tally = self.yearly_tally(year)
        if year_tally:
            res += f"Tallies for **Year {year}**"
            res += self.format_rank(self.rank(year_tally))
        else:
            res += f"No Data for **Year {year}**"
        
        return res

    @staticmethod
    def parse_params(message):
        if QuoteBot.validate_command(message):
            return message.split(" ")
        else:
            return None

    def random_greeting(self):
        return random.choice(self.greetings)

    @staticmethod
    def rank(counts):
        rank_ct = 1
        ranked = {}
        sor_ct = sorted(counts.items(), key=lambda i : i[1], reverse=True)
        for i, data in enumerate(sor_ct):
            if i > 0:
                if data[1] < sor_ct[i-1][1]:
                    rank_ct += 1
            if rank_ct not in ranked:
                ranked[rank_ct] = []
            ranked[rank_ct].append(data)
        return ranked

    def remove_quote(self, name, month, year):
        self.database.remove_quote(name, month, year)

    @staticmethod
    def validate_command(message):
        parts = message.split(" ")
        if message.startswith("$counts") or message.startswith("$tally"):
            if len(parts) >= 3:
                month = parts[1]
                year = parts[2]
                return month.isnumeric() and year.isnumeric()
        elif message.startswith("$dump") or message.startswith("$help"):
            return True
        elif message.startswith("$add") or message.startswith("$remove"):
            return len(parts) >= 2
        
        return False

    def yearly_tally(self, year):
        months = []
        year_tally = defaultdict(int)
        for month in range(1, 13):
            data = self.database.get_counts(month, year)
            if data:
                months.append(data)
        if len(months) > 0:
            for data in months:
                for name, ct in data.items():
                    year_tally[name] += ct
            return year_tally
