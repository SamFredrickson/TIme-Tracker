from collections import OrderedDict
from menu.actions.action import Action
from database.models.task import Task
from database.models.tags import Tags
from rich.prompt import Prompt
from rich import print
from datetime import datetime
from utils.date import get_time_pattern, parse_time_from_date, validate_date_pattern


class UpdateTask(Action):
    signs_and_words = [
        '-',
        'now'
    ]

    def __init__(self, menu) -> None:
        self.__menu = menu
        self.__task = Task()
        self.__tags = Tags()
        self.__name = 'update'

    def ask_and_validate(self, task: Task):
        start = parse_time_from_date(task.start)

        if task.end is not None:
            end = parse_time_from_date(task.end)
        if task.end is None:
            end = None

        old_description = task.description
        old_tags = None if ', '.join(task.tags) == '' else ', '.join(task.tags)

        date = Prompt.ask('Date', default=task.date_created)
        name = Prompt.ask('Task name', default=task.name)
        start = Prompt.ask('Task started', default=start)
        print('''\n[b][yellow]
        Tip: use '-' sign if you need to remove end-time and continue task
        Tip: use 'now' word to finish task with current time
        [/b]\n''')
        end = Prompt.ask('Task ended', default=end)
        tags = Prompt.ask('Tags', default=old_tags)
        description = Prompt.ask('Description', default=None)

        validated_date = validate_date_pattern(date)
        validated_start = validate_date_pattern(start, r'\d\d:\d\d:\d\d')

        if validated_date is False:
            self.__menu.warn('Invalid Date format. Example: 2022-02-02')
            return self.ask_and_validate(task)

        if validated_start is False:
            self.__menu.warn('Invalid Start format. Example: 00:30:00')
            return self.ask_and_validate(task)

        if end is not None and end not in self.signs_and_words:
            if validate_date_pattern(end, r'\d\d:\d\d:\d\d') is False:
                self.__menu.warn('Invalid End format. Example: 00:32:00')
                return self.ask_and_validate(task)
            end = f'{date} {end}'

        if end == '-':
            end = None

        current_time = datetime.now().strftime(get_time_pattern())
        if end == 'now':
            end = f'{date} {current_time}'

        if name is None:
            self.__menu.warn('Name is required')
            return self.ask_and_validate(task)

        start = f'{date} {start}'

        if description is None:
            description = old_description

        if tags is not None:
            tags = tags.split(',')
            tags = list(filter(lambda tag: tag != '', tags))
            if len(tags) == 0:
                self.__menu.warn(
                    'Tags list is empty. Example: cool, task, mytag')
                return self.ask_and_validate(task)

        return {
            "id": task.id,
            "ordered_dict": OrderedDict([('name', name), ('start', start), ('end', end), ('description', description), ('date_created', date)]),
            "tags": tags
        }

    def do(self, id: int):
        task = self.__task.get_by_id(id)
        if task is None:
            self.__menu.warn('Task does not exist')
            return False

        data = self.ask_and_validate(task)
        id = data['id']
        for field, value in data['ordered_dict'].items():
            self.__task.update(id, field, value)

        if data['tags'] is not None:
            self.__tags.recreate(id, data['tags'])

        self.__menu.render()
        item = self.__menu.ask_for_choice()
        self.__menu.call_action(item)

    @property
    def name(self):
        return self.__name
