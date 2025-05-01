import os
import logging
from pathlib import Path
from tkinter import messagebox
from scdatatools.sc import StarCitizen
from scdatatools.sc.blueprints.generators.datacore_entity import blueprint_from_datacore_entity
from config import Config

class Exporter:
    export_label = None
    export_log_filename = "export.log"

    def __init__(self, config: Config):
        try:
            self.sc = StarCitizen(config.SC_INSTALL_PATH, cache_dir=config.CACHE_DIR)
            print("Loading Datacore")
            assert self.sc.datacore is not None
        except Exception as e:
            messagebox.showerror("Failed to load StarCitizen data", str(e) + ". Please verify your settings.json file.")

        self.output_dir = Path(config.OUTPUT_DIR)

    def get_entities(self, filter=""):
        entities = {}
        for name, entity in self.sc.datacore.entities.items():
            category = self._get_category(entity.filename)
            if category and filter.lower() in name.lower():
                entities[name] = {"category": category}
        return entities

    def _get_category(self, filename: str):
        if filename.startswith("libs/foundry/records/entities/groundvehicles"):
            return "Vehicle"
        elif filename.startswith("libs/foundry/records/entities/spaceships"):
            return "Ship"
        return None

    def export_entity(self, entity_name: str, export_label):
        entity = self.sc.datacore.entities[entity_name]
        output_path = self.output_dir / entity.name
        output_path.mkdir(parents=True, exist_ok=True)

        self.export_label = export_label

        if os.path.isfile(self.export_log_filename):
            os.remove(self.export_log_filename)

        def exportprogress(msg="", progress: int=None, total: int=None, level=logging.INFO, exc_info=None):
            if msg != "":
                export_label.configure(text=msg)

            with open(self.export_log_filename, "a") as f:
                f.write(msg + "\n")

        print("Generating blueprint from entity")
        exportprogress(msg="Generating blueprint...")
        bp = blueprint_from_datacore_entity(self.sc, entity, monitor=exportprogress)

        exportprogress(msg="Saving blueprint...")
        with open(output_path / f"{bp.name}.scbp", "w") as f:
            bp.dump(f)

        print("Extracting blueprint")
        exportprogress(msg="Extracting blueprint...")
        bp.extract(outdir=output_path, auto_convert_textures=True, auto_convert_models=True, overwrite=True)
        print("Done!")