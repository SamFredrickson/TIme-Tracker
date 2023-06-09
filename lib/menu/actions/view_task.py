from menu.view_menu import ViewMenu
from menu.actions.action import Action
from menu.actions.update_task import UpdateTask
from database.types.task import Task as TaskType
from database.types.task_view import TaskViewType
from database.models.task import Task
from database.models.tags import Tags
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.prompt import Confirm

class ViewTask(Action):
    def __init__(self, menu, previous=None) -> None:
        self.__menu = menu
        self.__view_menu = ViewMenu(previous=previous)
        self.__task = Task()
        self.__tags = Tags()
        self.__previous = previous
        self.__console = Console()

    def get_formatted_list(self, task: TaskType):
        return TaskViewType(
            task.id, 
            task.name, 
            task.start, 
            task.end, 
            task.description, 
            task.date_created,
            task.tags
        ).get_props()

    def cli_do(self, id: int):
        task = self.__task.get_by_id(id)
        if not task:
            self.__menu.warn("Task does not exist")
            return False
        
        for item in self.get_formatted_list(task):
            print(item)

        view_menu = self.__view_menu.get_template()
        print(view_menu)
        item = self.__view_menu.ask_for_choice()

        if hasattr(item.action, 'name'):
             if item.action.name == 'delete':
                sure = Confirm.ask('Are you sure?')
                if sure:
                    self.__task.delete(id)
                    self.__tags.deleteByTaskId(id)

                self.__previous.render()
                item = self.__previous.ask_for_choice()
                self.__previous.call_action(item)
                return True
            
             if item.action.name == 'update':
                update_task = UpdateTask(menu=self.__previous)
                update_task.do(id=id)
                return True

        self.__view_menu.call_action(item)

    def do(self):
        id = Prompt.ask("Task number", default='1')
        task = self.__task.get_by_id(id)
        if not task:
            self.__menu.warn("Task does not exist")
            return self.do()
        
        for item in self.get_formatted_list(task):
            print(item)

        view_menu = self.__view_menu.get_template()
        print(view_menu)
        item = self.__view_menu.ask_for_choice()

        if hasattr(item.action, 'name'):
             if item.action.name == 'delete':
                print(f'[b]Task: [red]{task.id} - {task.name}[/b]')
                sure = Confirm.ask('Are you sure?')
                
                if sure:
                    self.__task.delete(id)
                    self.__tags.deleteByTaskId(id)

                self.__previous.render()
                item = self.__previous.ask_for_choice()
                self.__previous.call_action(item)
                return True
            
             if item.action.name == 'update':
                update_task = UpdateTask(menu=self.__previous)
                update_task.do(id=id)
                return True

        self.__previous.call_action(item)