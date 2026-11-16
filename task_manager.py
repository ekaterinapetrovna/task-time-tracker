
from database import Database


class TaskManager:
    """Управление задачами системы учёта времени."""

    STATUSES = ("Новая", "В работе", "Завершена")

    def __init__(self, database=None):
        self.db = database if database is not None else Database()

    def create_task(self, title, description=""):
        """Создание новой задачи."""

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Название задачи не может быть пустым")

        if not isinstance(description, str):
            raise ValueError("Описание должно быть строкой")

        task_id = self.db.execute(
            """
            INSERT INTO tasks (title, description, status)
            VALUES (?, ?, ?)
            """,
            (title.strip(), description.strip(), "Новая")
        )

        return self.get_task(task_id)

    def get_task(self, task_id):
        """Поиск задачи по идентификатору."""

        return self.db.fetch_one(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )

    def get_all_tasks(self):
        """Получение списка всех задач."""

        return self.db.fetch_all(
            "SELECT * FROM tasks ORDER BY id"
        )

    def update_status(self, task_id, new_status):
        """Изменение статуса существующей задачи."""

        task = self.get_task(task_id)

        if task is None:
            raise ValueError("Задача с таким ID не найдена")

        if new_status not in self.STATUSES:
            raise ValueError("Недопустимый статус задачи")

        self.db.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (new_status, task_id)
        )

        return self.get_task(task_id)

    def update_task(self, task_id, title, description=""):
        """Изменение названия и описания задачи."""

        if self.get_task(task_id) is None:
            raise ValueError("Задача с таким ID не найдена")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Название задачи не может быть пустым")

        if not isinstance(description, str):
            raise ValueError("Описание должно быть строкой")

        self.db.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?
            WHERE id = ?
            """,
            (title.strip(), description.strip(), task_id)
        )

        return self.get_task(task_id)

    def delete_task(self, task_id):
        """Удаление задачи и связанных рабочих сессий."""

        if self.get_task(task_id) is None:
            raise ValueError("Задача с таким ID не найдена")

        self.db.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        return True

    def get_tasks_by_status(self, status):
        """Получение задач с определённым статусом."""

        if status not in self.STATUSES:
            raise ValueError("Недопустимый статус задачи")

        return self.db.fetch_all(
            "SELECT * FROM tasks WHERE status = ? ORDER BY id",
            (status,)
        )
