import os
import requests
from datetime import datetime
import pytz

# Установка URL-адреса для API
TASKS_API_URL = 'https://json.medrating.org/todos'
USERS_API_URL = 'https://json.medrating.org/users'

# HTTP-запросы к API для получения данных о задачах и пользователях
response_tasks = requests.get(TASKS_API_URL)
response_users = requests.get(USERS_API_URL)

# Проверка выполнения запросов
try:
    tasks_data = response_tasks.json()
    users_data = response_users.json()
except requests.exceptions.RequestException as e:
    print(f'Ошибка при выполнении HTTP-запроса: {e}')
    exit()

# Создание директории
if not os.path.exists('tasks'):
    os.mkdir('tasks')

# Определение местного времени
local_timezone = pytz.timezone('Europe/Moscow')
current_time = datetime.now(local_timezone)

# Создания словаря для хранения данных отчетов в памяти
reports_data = {}

# Функция для создания текстового отчета для пользователя
def create_report(user_data, tasks_data):
    try:
        user_id = user_data.get('id')
        username = user_data.get('username')
        company_name = (user_data.get('company')).get('name')
        email = user_data.get('email')
    except TypeError as e:
        print(f'user_data должен быть словарем: {e}')

    # Формат имени файла
    file_name = f'tasks/{username}.txt'

    # Проверка на существование отчета
    if os.path.exists(file_name):
        try:
            # Переименование существующего файла
            old_file_name = f'tasks/old_{username}_{current_time.strftime("%Y-%m-%dT%H:%M")}.txt'
            os.rename(file_name, old_file_name)
        except OSError as e:
            try:
                old_file_name = f'tasks/old_{username}_{current_time.strftime("%Y-%m-%dTime%H_%M")}.txt'
                os.rename(file_name, old_file_name)
                print(f'Возможно вы используете не линукс? Выполнена обработка для Windows {e}')
            except OSError as e:
                print(f'Упс..., повторите попытку еще раз')


    try:
        # Список для хранения данных отчета
        report_data = []
        report_data.append(f'# Отчёт для {company_name}.')
        report_data.append(f'{user_data["name"]} <{email}> {current_time.strftime("%d.%m.%Y %H:%M")}')

        # Фильтр задач по пользователю
        try:
            user_tasks = [task for task in tasks_data if task.get('userId') == user_id]
        except TypeError as e:
            print(f'task_data должен быть словарем: {e}')

        total_tasks = len(user_tasks)

        report_data.append(f'Всего задач: {total_tasks}\n')

        if total_tasks == 0:
            report_data.append('У данного пользователя нет задач: ')
        else:
            # Разделение задач на актуальные и завершенные
            incomplete_tasks = [task for task in user_tasks if not task['completed']]
            completed_tasks = [task for task in user_tasks if task['completed']]

            report_data.append('## Актуальные задачи ({0}):'.format(len(incomplete_tasks)))
            for task in incomplete_tasks:
                task_title = task['title'][:46] + '...' if len(task['title']) > 46 else task['title']
                report_data.append(f'- {task_title}')

            report_data.append('\n## Завершённые задачи ({0}):'.format(len(completed_tasks)))
            for task in completed_tasks:
                task_title = task['title'][:46] + '...' if len(task['title']) > 46 else task['title']
                report_data.append(f'- {task_title}')

            # Сохранение отчета в словаре
            #print(reports_data[user_id])
            reports_data[user_id] = '\n'.join(report_data)

    except Exception as e:
        print(f'Непредвиденная ошибка при записи пользователя {username}: {e}')

# Создание и запись отчета для всех существующих(непустых) пользователей
for user in users_data:
    create_report(user, tasks_data)

    user_id = user['id']
    username = user['username']

    try:
        # Получить отчет из словаря или пустую строку, если отчета нет
        report_content = reports_data.get(user_id, '')
    except TypeError as e:
        print(f'reports_data должен быть словарем: {e}')

    if report_content:
            file_name = f'tasks/{username}.txt'
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(report_content)
