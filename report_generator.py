
import csv
from datetime import datetime
from pathlib import Path

from database import Database
from time_tracker import TimeTracker


class ReportGenerator:
    """Формирование отчётов по затраченному времени."""

    def __init__(self, database=None):
        self.db = database if database is not None else Database()
        self.tracker = TimeTracker(self.db)

    def get_report_data(self):
        """Получение статистики по всем задачам."""

        return self.db.fetch_all("""
            SELECT
                tasks.id,
                tasks.title,
                tasks.status,
                COUNT(time_sessions.id) AS sessions_count,
                COALESCE(SUM(time_sessions.duration), 0)
                    AS total_seconds
            FROM tasks
            LEFT JOIN time_sessions
                ON tasks.id = time_sessions.task_id
            GROUP BY tasks.id, tasks.title, tasks.status
            ORDER BY tasks.id
        """)

    def generate_text_report(self):
        """Формирование текстового отчёта."""

        data = self.get_report_data()

        lines = [
            "ОТЧЁТ ПО УЧЁТУ РАБОЧЕГО ВРЕМЕНИ",
            "=" * 45,
            f"Дата формирования: {datetime.now():%d.%m.%Y %H:%M}",
            ""
        ]

        for task in data:
            lines.extend([
                f"Задача №{task['id']}: {task['title']}",
                f"Статус: {task['status']}",
                f"Количество сессий: {task['sessions_count']}",
                "Затраченное время: "
                + self.tracker.format_duration(
                    task["total_seconds"]
                ),
                "-" * 45
            ])

        total = sum(task["total_seconds"] for task in data)

        lines.append(
            "Общее время по всем задачам: "
            + self.tracker.format_duration(total)
        )

        return "\n".join(lines)

    def save_txt(self, filename="time_report.txt"):
        """Сохранение отчёта в TXT."""

        report = self.generate_text_report()

        Path(filename).write_text(
            report,
            encoding="utf-8"
        )

        return filename

    def save_csv(self, filename="time_report.csv"):
        """Сохранение отчёта в CSV."""

        data = self.get_report_data()

        with open(
            filename, "w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file, delimiter=";")

            writer.writerow([
                "ID задачи",
                "Название",
                "Статус",
                "Количество сессий",
                "Затраченное время"
            ])

            for task in data:
                writer.writerow([
                    task["id"],
                    task["title"],
                    task["status"],
                    task["sessions_count"],
                    self.tracker.format_duration(
                        task["total_seconds"]
                    )
                ])

        return filename
