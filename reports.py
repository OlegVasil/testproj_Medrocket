import os
import requests
from datetime import datetime


def perform_request(url):
    try:
        response = requests.get(url)
        return response.json()
    except requests.exceptions.RequestException as re:
        print(f'Ошибка при выполнении HTTP-запроса: {re}')
        exit()


def is_valid_data(data):
    return all(isinstance(item, dict) for item in data)


def create_directory(directory_name):
    try:
        if not os.path.exists(directory_name):
            os.mkdir(directory_name)
    except PermissionError as pe:
        print(f'У Вас нет прав доступа на создание директории: {pe}')
        exit()


def get_user_tasks(user_id, tasks_data):
    user_tasks = []
    for task in tasks_data:
        if task.get('userId') == user_id:
            user_tasks.append(task)
    return user_tasks


def categorize_tasks(user_tasks):
    incomplete_tasks = []
    completed_tasks = []

    for task in user_tasks:
        if task['completed']:
            completed_tasks.append(task)
        else:
            incomplete_tasks.append(task)

    return completed_tasks, incomplete_tasks


# Функция для записи отчета в файл
def write_report_to_file(file_name, report_content, username, current_time):
    # Проверка на существование отчета
    old_file_name = ''
    if os.path.exists(file_name):
        if os.name == 'posix':
            old_file_name = f'tasks/old_{username}_{current_time.strftime("%Y-%m-%dT%H:%M")}.txt'
        elif os.name == 'nt':
            old_file_name = f'tasks/old_{username}_{current_time.strftime("%Y-%m-%dTime%H_%M")}.txt'
            print('Выполяется обработка для Windows')
        try:
            os.rename(file_name, old_file_name)
        except OSError as ose_t:
            print(f'Упс... повторите попытку еще раз: {ose_t}')
            exit()
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(report_content)
    except PermissionError as pe:
        print(f'У Вас нет прав доступа на запись файла: {pe}')
        exit()


# Функция для формирования текстового отчета для пользователя
def create_report(user_data, tasks_data, current_time):
    user_id = user_data.get('id')
    company_name = (user_data.get('company')).get('name')
    email = user_data.get('email')

    # Список для хранения данных отчета
    report_data = [f'# Отчёт для {company_name}.',
                   f'{user_data["name"]} <{email}> {current_time.strftime("%d.%m.%Y %H:%M")}']

    # Фильтр задач по пользователю
    user_tasks = get_user_tasks(user_id, tasks_data)
    total_tasks = len(user_tasks)

    report_data.append(f'Всего задач: {total_tasks}\n')
    if total_tasks == 0:
        report_data.append('## У данного пользователя нет задач')
        report_data.append('\n## Актуальные задачи (0)')
        report_data.append('\n## Завершённые задачи (0)')
    else:
        # Разделение задач на актуальные и завершенные
        completed_tasks, incomplete_tasks = categorize_tasks(user_tasks)

        # Формат актуальных задач
        report_data.append(f'## Актуальные задачи ({len(incomplete_tasks)}):')
        for task in incomplete_tasks:
            task_title = task['title'][:46] + '...' if len(task['title']) > 46 else task['title']
            report_data.append(f'- {task_title}')

        # Формат завершенных задач
        report_data.append(f'\n## Завершённые задачи ({len(completed_tasks)}):')
        for task in completed_tasks:
            task_title = task['title'][:46] + '...' if len(task['title']) > 46 else task['title']
            report_data.append(f'- {task_title}')

    user_report = '\n'.join(report_data)

    return user_report


def main():
    # Установка URL-адреса для API
    TASKS_API_URL = 'https://json.medrating.org/todos'
    USERS_API_URL = 'https://json.medrating.org/users'

    tasks_data = perform_request(TASKS_API_URL)
    users_data = perform_request(USERS_API_URL)

    if not is_valid_data(tasks_data) and not is_valid_data(users_data):
        print('Данные имеют неверный формат')
        exit()

    dir_name = 'tasks'
    create_directory(dir_name)

    # Создание и запись отчета для всех существующих(непустых) пользователей
    for user in users_data:
        current_time = datetime.now()
        report_content = create_report(user, tasks_data, current_time)
        username = user.get('username')

        if report_content:
            file_name = f'{dir_name}/{username}.txt'
            write_report_to_file(file_name, report_content, username, current_time)


if __name__ == '__main__':
    main()
