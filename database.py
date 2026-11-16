
import sqlite3


class Database:
    """Работа с базой данных системы учёта времени."""

    def __init__(self, db_path="task_tracker.db"):
        self.db_path = str(db_path)
        self.initialize()

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self):
        """Создание таблиц при первом запуске программы."""

        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'Новая'
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS time_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    duration REAL NOT NULL
                        CHECK(duration >= 0),
                    FOREIGN KEY (task_id)
                        REFERENCES tasks(id)
                        ON DELETE CASCADE
                )
            """)

            connection.commit()

    def execute(self, query, parameters=()):
        """Выполнение запроса на изменение данных."""

        with self.connect() as connection:
            cursor = connection.execute(query, parameters)
            connection.commit()
            return cursor.lastrowid

    def fetch_all(self, query, parameters=()):
        """Получение списка записей."""

        with self.connect() as connection:
            cursor = connection.execute(query, parameters)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query, parameters=()):
        """Получение одной записи."""

        with self.connect() as connection:
            cursor = connection.execute(query, parameters)
            row = cursor.fetchone()
            return dict(row) if row else None
