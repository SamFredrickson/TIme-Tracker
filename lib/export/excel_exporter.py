from typing import Dict, List
from .exporter import Exporter
from tracker.constants import export_dir
import xlsxwriter

class ExcelExporter(Exporter):
    format = 'xlsx'
    names = ['S. No.', 'Name', 'Started', 'Finished', 'Total', 'Description']
    formats = {}

    def __init__(self) -> None:
        super().__init__()

    def writeColumns(self, worksheet):
        for key, value in enumerate(self.names):
            worksheet.write(0, key, value, self.formats.get('header'))
    
    def writeRows(self, worksheet, data):
        column = 0
        row = 1

        for item in data:
            for _, value in item.items():
                worksheet.write(row, column, value, self.formats.get('text'))
                column += 1
            column = 0
            row += 1

    def write(self, fieldnames=List[str], data=Dict):
        name = self.generate_name()
        path = f'{export_dir}/{name}'
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()

        self.formats['header'] = workbook.add_format({
            "font": "Arial",
            "font_size": 14,
            "bold": True
        })

        self.formats['text'] = workbook.add_format({
            "font": "Arial",
            "font_size": 14,
        })    

        self.writeColumns(worksheet=worksheet)
        self.writeRows(worksheet=worksheet, data=data)

        worksheet.autofit()
        workbook.close()

        return name