from typing import Dict, List
import csv
from .exporter import Exporter
from tracker.constants import export_dir

class CsvExporter(Exporter):
    def __init__(self) -> None:
        super().__init__()

    def write(self, fieldnames=List[str], data=Dict):
        name = self.generate_name()
        
        with open(f'{export_dir}/{name}', 'wt') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
        return name