import os
import csv
import datetime
from config import LOG_BASE_DIR

class LogManager:
    def __init__(self):
        today = datetime.date.today()
        ym_str = today.strftime("%Y-%m")
        ymd_str = today.strftime("%Y-%m-%d")
        self.log_dir = os.path.join(LOG_BASE_DIR, ym_str)
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, f"{ymd_str}.csv")
        self.members = self._load()

    def _load(self):
        members = {}
        if os.path.exists(self.log_path):
            with open(self.log_path, "r", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if row:
                        members[row[0]] = ",".join(row[1:])
        return members

    def update(self, name, timestamp):
        if name in self.members:
            self.members[name] += "," + timestamp
        else:
            self.members[name] = timestamp

        self._save()

    def _save(self):
        with open(self.log_path, "w", encoding="utf-8") as f:
            for name, timestamps in sorted(self.members.items()):
                times = timestamps.split(',')[-4:]  # 最大4件
                f.write(name + "," + ",".join(times) + "\n")
