from datetime import datetime
from typing import Optional
import typer
import os

from menu.actions.show_tasks import ShowTasks
from database.types.date_range import DateRange
from export.csv_exporter import CsvExporter
from export.html_exporter import HtmlExporter
from export.excel_exporter import ExcelExporter
from utils.date import get_time_pattern, get_year_pattern, validate_date_pattern

from tracker.release import __app_name__, __version__
from tracker.constants import export_dir
from menu.main import Main
from menu.tasks import TasksMenu
from menu.actions.show_tasks import ShowTasks
from menu.actions.view_task import ViewTask
from menu.actions.delete_task import DeleteTask
from menu.actions.add_task import AddTask
from menu.actions.update_task import UpdateTask
from database.models.task import Task

app = typer.Typer()


@app.command(help='Shows main menu')
def menu():
    mainMenu = Main()
    mainMenu.render()
    item = mainMenu.ask_for_choice()
    mainMenu.call_action(item)


@app.command(help='Shows tasks list')
def task_list(
    date_from=typer.Option(datetime.now().strftime(
        get_year_pattern()), help="Date from, default today"),
    date_to=typer.Option(datetime.now().strftime(
        get_year_pattern()), help="Date to, default today"),
):
    main_menu = Main()
    tasks_menu = TasksMenu(main_menu)
    show_tasks = ShowTasks(tasks_menu)
    show_tasks.cli_do(date_from, date_to)


@app.command(help='View task info')
def task_view(id: int = typer.Option(..., help="Task id")):
    main_menu = Main()
    view_task = ViewTask(menu=main_menu, previous=main_menu)
    view_task.cli_do(id)


@app.command(help='Delete task')
def task_delete(id: int = typer.Option(..., help="Task id")):
    main_menu = Main()
    delete_action = DeleteTask(main_menu)
    delete_action.cli_do(id)


@app.command(help='Create task')
def task_create(
    date: str = typer.Option(datetime.now().strftime(
        get_year_pattern()), help="Date"),
    name: str = typer.Option(..., help="Task name"),
    start: str = typer.Option(datetime.now().strftime(
        get_time_pattern()), help="Task start"),
    end: str = typer.Option(None, help="Task end"),
    description: str = typer.Option(None, help="Description"),
    tags: str = typer.Option(None, help="Tags")
):
    main_menu = Main()
    add_action = AddTask(main_menu)
    id = add_action.do_cli(date, name, start, end, description, tags)

    if id:
        main_menu.success(f'Task number {id} successfully created')
        return True


@app.command(help='Update task')
def task_update(id: int = typer.Option(..., help="Task id")):
    main_menu = Main()
    update_acition = UpdateTask(main_menu)
    update_acition.do(id=id)


@app.command(help='Stop running task')
def task_stop(
    id: int = typer.Option(..., help="Task id"),
    time: str = typer.Option(datetime.now().strftime(
        get_time_pattern()), help='Stop time with specific time')
):
    main_menu = Main()
    model = Task()
    task = model.get_by_id(id)
    if task is None:
        main_menu.warn('Task does not exist')
        return False
    validated_time = validate_date_pattern(time, r'\d\d:\d\d:\d\d')
    if validated_time is False:
        main_menu.warn('Invalid Time format. Example: 00:30:00')
        return False
    model.update(id, 'end', f'{task.date_created} {time}')
    main_menu.success(f'Finish time ({time}) successfully set')


@app.command(help='Continue task you stopped before')
def task_continue(
    id: int = typer.Option(..., help="Task id")
):
    main_menu = Main()
    model = Task()
    task = model.get_by_id(id)

    if task is None:
        main_menu.warn('Task does not exist')
        return False

    if task.end is None:
        main_menu.warn('This task is still in progress')
        return False

    model.add(
        name=task.name,
        description=task.description,
        date_created=task.date_created
    )

    main_menu.success('New task with a new time created successfully')


@app.command(help='Export tasks to file')
def task_export(
    date_from: str = typer.Option(datetime.now().strftime(
        get_year_pattern()), help="Date from, default today"),
    date_to: str = typer.Option(datetime.now().strftime(
        get_year_pattern()), help="Date to, default today"),
    type: str = typer.Option('excel', help="File format (csv, html, excel)"),
    tags: str = typer.Option(None, help="Tags")
):
    main_menu = Main()

    validated_from = validate_date_pattern(date_from)
    validated_to = validate_date_pattern(date_to)

    if validated_from is False or validated_to is False:
        main_menu.warn('Invalid date format. Example: 2022-02-02')
        return False

    date_range = DateRange(date_from=date_from, date_to=date_to)

    if type == 'csv':
        task = Task()
        csv_exporter = CsvExporter()

        tasks = task.get_tasks_for_csv(
            date_range=date_range, 
            tags=tags
        )
        
        name = csv_exporter.write(fieldnames=tasks['fieldnames'], data=tasks['data'])
    
    if type == 'excel':
        task = Task()
        excel_exporter = ExcelExporter()

        tasks = task.get_tasks_for_csv(
            date_range=date_range, 
            tags=tags
        )
        
        name = excel_exporter.write(fieldnames=tasks['fieldnames'], data=tasks['data'])

    if type == 'html':
        task = Task()
        html_exporter = HtmlExporter()

        tasks = task.get_tasks_for_html(date_range=date_range, tags=tags)
        name = html_exporter.write(tasks=tasks)

    main_menu.success(f'Tasks successully exported to {export_dir}/{name}')


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True
    )
) -> None:
    return
