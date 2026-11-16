
import tempfile
import unittest
from pathlib import Path

from database import Database
from task_manager import TaskManager
from time_tracker import TimeTracker
from report_generator import ReportGenerator


class FakeClock:
    """Управляемые часы для тестирования таймера."""

    def __init__(self):
        self.current = 100.0

    def __call__(self):
        return self.current

    def advance(self, seconds):
        self.current += seconds


class TestTimeTrackingSystem(unittest.TestCase):

    def setUp(self):
        """Подготовка отдельной базы для каждого теста."""

        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"

        self.db = Database(db_path)
        self.manager = TaskManager(self.db)
        self.clock = FakeClock()
        self.tracker = TimeTracker(self.db, clock=self.clock)
        self.reports = ReportGenerator(self.db)

        self.task = self.manager.create_task(
            "Подготовка аналитического отчёта",
            "Анализ данных и оформление результатов"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_task(self):
        """Проверка создания задачи."""

        self.assertEqual(
            self.task["title"],
            "Подготовка аналитического отчёта"
        )
        self.assertEqual(self.task["status"], "Новая")

    def test_empty_title(self):
        """Запрет создания задачи без названия."""

        with self.assertRaises(ValueError):
            self.manager.create_task("   ")

    def test_update_status(self):
        """Проверка изменения статуса."""

        updated = self.manager.update_status(
            self.task["id"], "В работе"
        )
        self.assertEqual(updated["status"], "В работе")

    def test_start_timer(self):
        """Проверка запуска таймера."""

        self.tracker.start_timer(self.task["id"])

        self.assertIn(
            self.task["id"],
            self.tracker.active_timers
        )

    def test_stop_timer(self):
        """Проверка остановки таймера."""

        self.tracker.start_timer(self.task["id"])
        self.clock.advance(125)

        duration = self.tracker.stop_timer(self.task["id"])

        self.assertEqual(duration, 125)
        self.assertEqual(
            self.tracker.get_total_time(self.task["id"]),
            125
        )

    def test_multiple_sessions(self):
        """Суммирование нескольких рабочих сессий."""

        task_id = self.task["id"]

        self.tracker.start_timer(task_id)
        self.clock.advance(60)
        self.tracker.stop_timer(task_id)

        self.tracker.start_timer(task_id)
        self.clock.advance(90)
        self.tracker.stop_timer(task_id)

        self.assertEqual(
            self.tracker.get_total_time(task_id),
            150
        )
        self.assertEqual(
            len(self.tracker.get_sessions(task_id)),
            2
        )

    def test_duplicate_start(self):
        """Запрет повторного запуска таймера."""

        self.tracker.start_timer(self.task["id"])

        with self.assertRaises(ValueError):
            self.tracker.start_timer(self.task["id"])

    def test_stop_without_start(self):
        """Запрет остановки неактивного таймера."""

        with self.assertRaises(ValueError):
            self.tracker.stop_timer(self.task["id"])

    def test_completed_task(self):
        """Запрет запуска таймера завершённой задачи."""

        self.manager.update_status(
            self.task["id"], "Завершена"
        )

        with self.assertRaises(ValueError):
            self.tracker.start_timer(self.task["id"])

    def test_time_format(self):
        """Проверка форматирования времени."""

        self.assertEqual(
            TimeTracker.format_duration(3665),
            "01:01:05"
        )

    def test_report_data(self):
        """Проверка статистики отчёта."""

        self.tracker.start_timer(self.task["id"])
        self.clock.advance(120)
        self.tracker.stop_timer(self.task["id"])

        data = self.reports.get_report_data()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["sessions_count"], 1)
        self.assertEqual(data[0]["total_seconds"], 120)

    def test_save_reports(self):
        """Проверка сохранения TXT и CSV."""

        folder = Path(self.temp_dir.name)

        txt_path = folder / "report.txt"
        csv_path = folder / "report.csv"

        self.reports.save_txt(txt_path)
        self.reports.save_csv(csv_path)

        self.assertTrue(txt_path.exists())
        self.assertTrue(csv_path.exists())

    def test_data_persistence(self):
        """Проверка сохранения задач в SQLite."""

        another_manager = TaskManager(
            Database(self.db.db_path)
        )

        saved_task = another_manager.get_task(
            self.task["id"]
        )

        self.assertEqual(
            saved_task["title"],
            self.task["title"]
        )


if __name__ == "__main__":
    unittest.main()
