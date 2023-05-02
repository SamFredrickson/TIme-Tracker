import os
from datetime import datetime
from tracker.constants import export_dir

class Exporter:
    folder_name = 'export'
    format = 'csv'

    def __init__(self) -> None:
        if not os.path.exists(export_dir):
            os.makedirs(export_dir, 0o744)

    def generate_name(self):
        '''generate name for future file in export folder'''
        date = datetime.now().strftime( "%Y_%m_%d" )
        time = datetime.now().strftime( "%H_%M_%S" )
        return f'export_{date}_{time}.{self.format}'