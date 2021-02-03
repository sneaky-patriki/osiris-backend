from time import time
from data_store import database, Taskgroup
from error import InputError, AccessError, DependencyError
import tasks

def add(token, topic_id, name, submit_multiple):
    auth.authorise_user(token)

    taskgroup_id = database.generate_id('taskgroup')

    new_taskgroup = Taskgroup(taskgroup_id, topic_id, name, submit_multiple)
    database.taskgroups.append(new_taskgroup)

    for topic in database.topics:
        if topic.topic_id == topic_id:
            topic.taskgroups.append(taskgroup_id)

    database.update()
    return new_taskgroup.json()

def edit(token, taskgroup_id, name):
    auth.authorise_user(token)

    for taskgroup in database.taskgroups:
        if taskgroup.taskgroup_id == taskgroup_id:
            taskgroup.name = name
            taskgroup.modified = time()
            break

    database.update()
    return taskgroup.json()

def move(token, taskgroup_id, new_topic_id):
    auth.authorise_user(token)

    for topic in database.topics:
        if taskgroup_id in topic.taskgroups:
            topic.taskgroups.remove(taskgroup_id)
        elif topic.topic_id == new_topic_id:
            topic.taskgroups.append(taskgroup_id)

    for taskgroup in database.taskgroups:
        if taskgroup.taskgroup_id == taskgroup_id:
            taskgroup.topic_id = new_topic_id

    database.update()

    return {}


def delete(token, taskgroup_id):
    auth.authorise_user(token)

    for task in database.tasks:
        if task.taskgroup_id == taskgroup_id:
            raise DependencyError('Task group must be empty to be deleted')

    for taskgroup in database.taskgroups:
        if taskgroup.taskgroup_id == taskgroup_id:
            database.taskgroups.remove(taskgroup)

            for topic in database.topics:
                if topic.topic_id == taskgroup.topic_id:
                    topic.taskgroups.remove(taskgroup_id)
            break

    database.update()


def listall(topic_id, taskgroup_ids):
    taskgroups = []
    for taskgroup in database.taskgroups:
        if taskgroup.topic_id == topic_id:
            taskgroup_details = taskgroup.json()
            taskgroup_details['tasks'] = tasks.listall(taskgroup.taskgroup_id, taskgroup.tasks)
            taskgroups.append(taskgroup_details)

    taskgroups.sort(key=lambda tg: taskgroup_ids.index(tg['taskgroup_id']))
    return taskgroups

def details(token, taskgroup_id):
    for taskgroup in database.taskgroups:
        if taskgroup.taskgroup_id == taskgroup_id:
            taskgroup_details = taskgroup.json()

            for topic in database.topics:
                if topic.topic_id == taskgroup.topic_id:
                    taskgroup_details['topic'] = {'topic_id': topic.topic_id, 'name': topic.name}

            taskgroup_details['tasks'] = []
            for task in database.tasks:
                if task.taskgroup_id == taskgroup_id:
                    taskgroup_details['tasks'].append(task.json())

            return {'taskgroup': taskgroup_details}

def reorder(token, topic_id, new_taskgroups):
    for topic in database.topics:
        if topic.topic_id == topic_id:
            topic.taskgroups = new_taskgroups
            topic.modified = time()

    database.update()

    return {}
