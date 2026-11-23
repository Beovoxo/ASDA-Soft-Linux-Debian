import csv
import json
from pathlib import Path

class ParameterStore:
    """Stores documented parameter values; does not invent parameter IDs."""
    def __init__(self):
        self.rows = []

    def load_json(self, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON root must be a list of parameter records")
        self.rows = data

    def save_json(self, path):
        Path(path).write_text(json.dumps(self.rows, indent=2, ensure_ascii=False),
                              encoding="utf-8")

    def load_csv(self, path):
        with open(path, newline="", encoding="utf-8-sig") as f:
            self.rows = list(csv.DictReader(f))

    def save_csv(self, path):
        fields = ["parameter", "name", "value", "unit", "description"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.rows)
