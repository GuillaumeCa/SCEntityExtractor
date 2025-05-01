import os
from pathlib import Path
from tkinter import messagebox
from scdatatools.sc import StarCitizen
from scdatatools.sc.blueprints.generators.datacore_entity import blueprint_from_datacore_entity
from config import Config

class Exporter:
    def __init__(self, config: Config):
        try:
            self.sc = StarCitizen(config.SC_INSTALL_PATH, cache_dir=config.CACHE_DIR)
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

    def export_entity(self, entity_name: str):
        entity = self.sc.datacore.entities[entity_name]
        output_path = self.output_dir / entity.name
        output_path.mkdir(parents=True, exist_ok=True)

        bp = blueprint_from_datacore_entity(self.sc, entity)
        with open(output_path / f"{bp.name}.scbp", "w") as f:
            bp.dump(f)

        bp.extract(outdir=output_path, auto_convert_textures=True, auto_convert_models=True, overwrite=True)