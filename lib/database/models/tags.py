from tracker.database import database
from database.models.model import Model
from typing import List

class Tags(Model):
    def __init__(self) -> None:
        self.__cursor = database.cursor
        self.__connnection = database.connection
        self.__table = 'tags'
    
    def add(self, taskId: int, names: List[str]):
        for name in names:
            query = f'''
                INSERT INTO {self.__table} (taskId, name)
                VALUES (?, ?) 
            '''
            self.__cursor.execute(query, (taskId, name.strip()))
            self.__connnection.commit()
        return True
    
    def getByTaskId(self, taskId: int):
        query = f'''
               SELECT * FROM {self.__table}
               WHERE taskId = ?
            '''
        self.__cursor.execute(query, (taskId,))
        self.__connnection.commit()
        tags = self.__cursor.fetchall()
        result = []
        for tag in tags:
            id, taskId, name = tag
            result.append(name)
        return result

    def deleteByTaskId(self, taskId: int):
        query = f'''
            DELETE FROM {self.__table}
            WHERE taskId = ?
        '''
        self.__cursor.execute(query, (taskId, ))
        self.__connnection.commit()
        return taskId
    
    def recreate(self, taskId: int, names: List[str]):
        self.deleteByTaskId(taskId=taskId)
        for name in names:
            query = f'''
                INSERT INTO {self.__table} (taskId, name)
                VALUES (?, ?) 
            '''
            self.__cursor.execute(query, (taskId, name.strip()))
            self.__connnection.commit()
        return True