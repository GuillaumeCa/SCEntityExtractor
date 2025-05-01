import json
from pathlib import Path

class Config:
    CONFIG_FILE = Path("settings.json")

    SC_INSTALL_PATH = "C:/Program Files/Roberts Space Industries/StarCitizen/LIVE"
    CACHE_DIR = ".sccache"
    OUTPUT_DIR = "./extract"

    def load(self):
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.SC_INSTALL_PATH = data.get("SC_path", self.SC_INSTALL_PATH)
        else:
            self.save()

    def save(self):
        with open(self.CONFIG_FILE, "w") as f:
            json.dump({"SC_path": self.SC_INSTALL_PATH}, f, indent=4)