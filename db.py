import sqlite3
from singletone import MetaSingleton


class Database(metaclass=MetaSingleton):
    conn = None

    def __init__(self, name):
        self.name = name

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.name)
            self.curs = self.conn.cursor()
        return self.curs