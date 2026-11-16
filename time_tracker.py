
import time
from datetime import datetime, timezone

from database import Database
from task_manager import TaskManager


class TimeTracker:
    """Учёт времени выполнения задач."""

    def __init__(self, database=None, clock=None):
        self.db = database if database is not None else Database()
        self.tasks = TaskManager(self.db)
        self.clock = clock if clock is not None else time.monotonic
        self.active_timers = {}

    def start_timer(self, task_id):
        """Запуск таймера для выбранной задачи."""

        task = self.tasks.get_task(task_id)

        if task is None:
            raise ValueError("Задача не найдена")

        if task["status"] == "Завершена":
            raise ValueError(
                "Нельзя запустить таймер завершённой задачи"
            )

        if task_id in self.active_timers:
            raise ValueError("Таймер этой задачи уже запущен")

        self.active_timers[task_id] = (
            self.clock(),
            datetime.now(timezone.utc).isoformat()
        )

        self.tasks.update_status(task_id, "В работе")

        return f"Таймер задачи №{task_id} запущен"

    def stop_timer(self, task_id):
        """Остановка таймера и сохранение сессии."""

        if task_id not in self.active_timers:
            raise ValueError("Таймер задачи не запущен")

        start_monotonic, start_time = self.active_timers[task_id]

        duration = max(0.0, self.clock() - start_monotonic)
        end_time = datetime.now(timezone.utc).isoformat()

        self.db.execute(
            """
            INSERT INTO time_sessions
                (task_id, start_time, end_time, duration)
            VALUES (?, ?, ?, ?)
            """,
            (task_id, start_time, end_time, duration)
        )

        del self.active_timers[task_id]

        return duration

    def get_total_time(self, task_id):
        """Общее затраченное время по задаче."""

        if self.tasks.get_task(task_id) is None:
            raise ValueError("Задача не найдена")

        result = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(duration), 0) AS total
            FROM time_sessions
            WHERE task_id = ?
            """,
            (task_id,)
        )

        return float(result["total"])

    def get_sessions(self, task_id):
        """История рабочих сессий задачи."""

        if self.tasks.get_task(task_id) is None:
            raise ValueError("Задача не найдена")

        return self.db.fetch_all(
            """
            SELECT *
            FROM time_sessions
            WHERE task_id = ?
            ORDER BY id
            """,
            (task_id,)
        )

    @staticmethod
    def format_duration(seconds):
        """Преобразование секунд в часы, минуты и секунды."""

        total_seconds = int(seconds)

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
