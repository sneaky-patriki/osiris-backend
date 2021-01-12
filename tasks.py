from time import time
from data_store import database, Task
from error import InputError, AccessError

def add(token, taskgroup_id, name, difficulty, type, description, hint, solution):
    database.authorise_user(token)

    task_id = database.generate_id('task')

    for taskgroup in database.taskgroups:
        if taskgroup.taskgroup_id == taskgroup_id and taskgroup.submit_multiple and type != 'standard':
            raise InputError('Only standard tasks are allowed for taskgroups where you can submit for multiple tasks.')

    new_task = Task(task_id, taskgroup_id, name, difficulty, type,
                    description, hint, solution)
    database.tasks.append(new_task)

    for taskgroup in database.taskgroups:
        if taskgroup.taskgroup_id == taskgroup_id:
            taskgroup.tasks.append(task_id)

    database.update()
    return new_task.json()

def edit(token, task_id, name, difficulty, description, hint, solution, choices, correct_answers):
    database.authorise_user(token)

    for task in database.tasks:
        if task.task_id == task_id:
            task.name = name
            task.difficulty = difficulty
            task.description = description
            task.hint = hint
            task.solution = solution
            task.modified = time()
            task.choices = choices

            if task.answer_type == 'multiple-choice-single':
                task.correct_answer = int(correct_answers[0])
            elif task.answer_type == 'multiple-choice-multiple':
                task.correct_answer = list(map(int, correct_answers))

            database.update()
            return {'task': task.json()}

def add_attachment(token, task_id, name, attachment):
    pass

def delete(token, task_id):
    database.authorise_user(token)

    for task in database.tasks:
        if task.task_id == task_id:
            database.tasks.remove(task)

            for taskgroup in database.taskgroups:
                if taskgroup.taskgroup_id == task.taskgroup_id:
                    taskgroup.tasks.remove(task_id)

            break

    database.update()

def move(token, task_id, new_taskgroup_id):
    for taskgroup in database.taskgroups:
        if task_id in taskgroup.tasks:
            taskgroup.tasks.remove(task_id)
        elif taskgroup.taskgroup_id == new_taskgroup_id:
            taskgroup.tasks.append(task_id)

    for task in database.tasks:
        if task.task_id == task_id:
            task.taskgroup_id = new_taskgroup_id

    database.update()

    return {}

def reorder(token, taskgroup_id, new_tasks):
    for taskgroup in database.taskgroups:
        if taskgroup.taskgroup_id == taskgroup_id:
            taskgroup.tasks = new_tasks
            taskgroup.modified = time()

    database.update()

    return {}

def listall(taskgroup_id, task_ids):
    task_details = []
    for task in database.tasks:
        if task.taskgroup_id == taskgroup_id:
            task_detail = task.json()

            for taskgroup in database.taskgroups:
                if taskgroup.taskgroup_id == taskgroup_id:
                    task_detail['submit_multiple'] = taskgroup.submit_multiple
                    task_detail['taskgroup_name'] = taskgroup.name

                    task_details.append(task_detail)
                    break


    task_details.sort(key=lambda tk: task_ids.index(tk['task_id']))
    return task_details

def details(token, task_id):
    database.authorise_user(token)

    for task in database.tasks:
        if task.task_id == task_id:
            task_details = task.json()
            task_details['attachments'] = []

            for taskgroup in database.taskgroups:
                if taskgroup.taskgroup_id == task.taskgroup_id:
                    task_details['taskgroup'] = taskgroup.name
                    task_details['submit_multiple'] = taskgroup.submit_multiple

            for attachment in database.attachments:

                if attachment.attachment_id in task.attachments:
                    task_details['attachments'].append(
                        {'attachment_id': attachment.attachment_id,
                         'cover_name': attachment.cover_name,
                         'url':f'http://127.0.0.1:8080/tasks/attachments/retrieve?attachment_id={attachment.attachment_id}'
                    })

            return {'task': task_details}
