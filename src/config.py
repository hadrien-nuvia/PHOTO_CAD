from pathlib import Path
import yaml

class Config:
    def __init__(self, config_file: str = 'examples/sample_config.yaml'):
        self.config_file = Path(config_file)
        self.default_config = {
            'image_processing': {
                'resize': (1024, 768),
                'threshold': 128,
            },
            'line_detection': {
                'method': 'canny',
                'low_threshold': 50,
                'high_threshold': 150,
            },
            'snapping': {
                'snap_to_grid': True,
                'grid_size': 10,
            },
            'output': {
                'dxf_file': 'output.dxf',
                'geojson_file': 'output.geojson',
            }
        }
        self.config = self.load_config()

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        return self.default_config

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value

    def save(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)