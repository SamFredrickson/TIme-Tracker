from typing import List
from utils.date import get_difference, get_formatted_total
from .exporter import Exporter
from database.types.task import Task as TaskType
from .templates.content import content
from .templates.main import main
from tracker.constants import export_dir

class HtmlExporter(Exporter):
    format = 'html'

    def __init__(self) -> None:
        super().__init__()

    def write(self, tasks=List[TaskType]):
        content_concatinated = ''

        total_days = 0
        total_hours = 0
        total_minutes = 0
        total_seconds = 0

        for task in tasks:
            difference = get_difference(task.start, task.end)
            total_days += difference['days']
            total_hours += difference['hours']
            total_minutes += difference['minutes']
            total_seconds += difference['seconds']

            content_concatinated += content.format(
                id=task.id,
                name=task.name,
                start=task.start,
                end=task.end,
                total=task.difference,
                description=task.description
            )

        content_concatinated += content.format(
                id='—',
                name='—',
                start='—',
                end='—',
                total=get_formatted_total(total_days, total_hours, total_minutes, total_seconds),
                description='—'
            )
        
        name = self.generate_name()
        template_formatted = main.format(
            content=content_concatinated,
        )

        with open(f'{export_dir}/{name}', 'wt') as file:
            file.write(template_formatted)
        
        return name