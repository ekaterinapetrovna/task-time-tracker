
from database import Database
from task_manager import TaskManager
from time_tracker import TimeTracker
from report_generator import ReportGenerator


def show_menu():
    """Отображение главного меню."""

    print("\n" + "=" * 45)
    print("СИСТЕМА УЧЁТА РАБОЧЕГО ВРЕМЕНИ")
    print("=" * 45)
    print("1. Создать задачу")
    print("2. Просмотреть список задач")
    print("3. Изменить статус задачи")
    print("4. Запустить таймер")
    print("5. Остановить таймер")
    print("6. Посмотреть время по задаче")
    print("7. Посмотреть общий отчёт")
    print("8. Сохранить отчёт в TXT")
    print("9. Сохранить отчёт в CSV")
    print("0. Выход")
    print("=" * 45)


def main():
    """Запуск системы управления задачами."""

    db = Database()
    manager = TaskManager(db)
    tracker = TimeTracker(db)
    reports = ReportGenerator(db)

    while True:
        show_menu()
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                title = input("Название задачи: ")
                description = input("Описание: ")

                task = manager.create_task(title, description)

                print(f"Задача №{task['id']} создана!")

            elif choice == "2":
                tasks = manager.get_all_tasks()

                if not tasks:
                    print("Список задач пуст.")

                for task in tasks:
                    print(
                        f"№{task['id']} | {task['title']} "
                        f"| {task['status']}"
                    )

            elif choice == "3":
                task_id = int(input("ID задачи: "))

                print("Статусы: Новая, В работе, Завершена")
                status = input("Новый статус: ")

                if (
                    status == "Завершена"
                    and task_id in tracker.active_timers
                ):
                    raise ValueError(
                        "Сначала остановите таймер задачи"
                    )

                manager.update_status(task_id, status)
                print("Статус обновлён!")

            elif choice == "4":
                task_id = int(input("ID задачи: "))
                print(tracker.start_timer(task_id))

            elif choice == "5":
                task_id = int(input("ID задачи: "))
                duration = tracker.stop_timer(task_id)

                print(
                    "Время сессии: "
                    + tracker.format_duration(duration)
                )

            elif choice == "6":
                task_id = int(input("ID задачи: "))
                total = tracker.get_total_time(task_id)

                print(
                    "Общее время: "
                    + tracker.format_duration(total)
                )

            elif choice == "7":
                print(reports.generate_text_report())

            elif choice == "8":
                filename = reports.save_txt()
                print(f"Отчёт сохранён: {filename}")

            elif choice == "9":
                filename = reports.save_csv()
                print(f"Отчёт сохранён: {filename}")

            elif choice == "0":
                if tracker.active_timers:
                    print(
                        "Сначала остановите все активные таймеры."
                    )
                    continue

                print("Работа программы завершена.")
                break

            else:
                print("Неизвестная команда. Попробуйте снова.")

        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
