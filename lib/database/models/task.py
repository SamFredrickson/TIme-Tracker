from datetime import datetime
from tracker.database import database
from database.models.model import Model
from database.types.date_range import DateRange
from database.types.task import Task as TaskType
from database.models.tags import Tags
from utils.date import get_difference, get_formatted_total, get_year_pattern, get_datetime_pattern, get_formatted_difference
from utils.sql import generateQuestionMarksForIn


class Task(Model):
    def __init__(self) -> None:
        self.__cursor = database.cursor
        self.__connnection = database.connection
        self.__table = 'tasks'

    def is_task_exists_for_date(self, date: str, name: str):
        query = f'''
               SELECT * FROM tasks 
               WHERE date_created = ?
               AND name = ?
            '''
        self.__cursor.execute(query, (date, name))
        self.__connnection.commit()
        task = self.__cursor.fetchone()
        return task

    def get_tasks(self, date_range: DateRange):
        task_list = []
        query = f'''
               SELECT * FROM tasks 
               WHERE date_created >= ?
               AND date_created <= ?
            '''

        self.__cursor.execute(
            query, (date_range.date_from, date_range.date_to))
        self.__connnection.commit()
        tasks = self.__cursor.fetchall()

        for task in tasks:
            id, name, start, end, description, date_created = task
            task_list.append(
                TaskType
                (
                    id=id,
                    name=name,
                    start=start,
                    end=end,
                    description=description,
                    date_created=date_created
                )
            )

        return task_list

    def get_tasks_for_html(
        self,
        date_range: DateRange,
        name=None
    ):
        task_list = []
        execute_fields = (
            date_range.date_from,
            date_range.date_to
        )

        query = f'''
               SELECT * FROM tasks 
               WHERE date_created >= ?
               AND date_created <= ?
            '''

        if name is not None:
            query += ' AND name = ?'
            execute_fields = (
                date_range.date_from,
                date_range.date_to,
                name
            )

        self.__cursor.execute(query, execute_fields)
        self.__connnection.commit()
        tasks = self.__cursor.fetchall()

        for task in tasks:
            id, name, start, end, description, date_created = task
            task_list.append(
                TaskType(
                    id=id,
                    name=name,
                    start=start,
                    end=end,
                    description=description,
                    date_created=date_created
                )
            )

        return task_list

    def get_tasks_for_csv(
        self,
        date_range: DateRange,
        name=None,
        tags=None
    ):
        task_list = []
        execute_fields = (
            date_range.date_from,
            date_range.date_to
        )

        query = f'''
               SELECT 
                     DISTINCT task.id, task.name, task.start, task.end, task.date_created, task.description 
               FROM tasks task
                    JOIN tags tag ON tag.taskId = task.id
                    WHERE (task.date_created >= ?
               AND task.date_created <= ?)
            '''

        if tags is not None:
            tags = tags.split(',')
            length = len(tags)
            marks = generateQuestionMarksForIn(length=length)
            query += ' AND tag.name in ' + marks

            execute_fields = [
                date_range.date_from,
                date_range.date_to,
            ]

            execute_fields += [tag.strip() for tag in tags]

        self.__cursor.execute(query, execute_fields)
        self.__connnection.commit()
        tasks = self.__cursor.fetchall()

        fieldnames = ['S. No.', 'Name', 'Started',
                      'Finished', 'Total', 'Description']
        total_days = 0
        total_hours = 0
        total_minutes = 0
        total_seconds = 0

        for task in tasks:
            id, name, start, end, description, date_created = task

            difference = get_difference(start, end)
            total_days += difference['days']
            total_hours += difference['hours']
            total_minutes += difference['minutes']
            total_seconds += difference['seconds']

            task_list.append({
                'S. No.': id,
                'Name': name,
                'Started': start,
                'Finished': end,
                'Total': get_formatted_difference(start, end),
                'Description': description
            })

        task_list.append({
            'S. No.': '—',
            'Name': '—',
            'Started': '—',
            'Finished': '—',
            'Total': get_formatted_total(total_days, total_hours, total_minutes, total_seconds),
            'Description': '—'
        })

        return {
            "fieldnames": fieldnames,
            "data": task_list
        }

    def get_by_id(self, id):
        query = f'''
            SELECT * FROM {self.__table}
            WHERE id = ?
        '''
        self.__cursor.execute(query, (id, ))
        self.__connnection.commit()
        task = self.__cursor.fetchone()
        if not task:
            return task

        id, name, start, end, description, date_created = task
        tagsModel = Tags()
        tags = tagsModel.getByTaskId(id)

        return TaskType(
            id=id,
            name=name,
            start=start,
            end=end,
            description=description,
            date_created=date_created,
            tags=tags
        )

    def delete(self, id):
        query = f'''
            DELETE FROM {self.__table}
            WHERE id = ?
        '''
        self.__cursor.execute(query, (id, ))
        self.__connnection.commit()
        return id

    def add(
        self,
        name: str,
        start=datetime.now().strftime(get_datetime_pattern()),
        end=None,
        description=None,
        date_created=datetime.now().strftime(get_year_pattern()),
        tags=None
    ):
        query = f'''
                INSERT INTO {self.__table} (name, start, end, description, date_created)
                VALUES (?, ?, ?, ?, ?) 
            '''
        self.__cursor.execute(
            query, (name, start, end, description, date_created))
        self.__connnection.commit()
        taskId = self.__cursor.lastrowid

        if tags is not None:
            tagsModel = Tags()
            tagsModel.add(taskId=taskId, names=tags)

        return taskId

    def update(self, id, field, value):
        query = f'''
            UPDATE {self.__table} SET {field} = ? WHERE id = ?
        '''
        self.__cursor.execute(query, (value, id))
        self.__connnection.commit()
        return self.__cursor.lastrowid
