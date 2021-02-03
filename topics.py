from time import time
from data_store import database, Topic
from models import Topic, Course
from error import InputError, AccessError, DependencyError
import taskgroups
import auth
from models import Topic, Course

def listall(token):
    auth.authorise_user(token)

    topics = list(Topic.select().dicts())
    print(topics)
    for topic in topics:
        topic['courses'] = []
    '''
    topics = []
    for topic in database.topics:
        topic_details = topic.json()

        topic_details['courses'] = []
        for module in database.modules:
            if module.topic == topic.topic_id:
                for course in database.courses:
                    if course.course_id == module.course:
                        topic_details['courses'].append({'course_id':module.course, 'name':course.name})

        topics.append(topic_details)
    '''

    return {'topics': topics, 'currentTime': time()}

def add(token, name):
    auth.authorise_user(token)

    topic = Topic.create(name=name, modified=time())

    return {'topic_id':topic.id, 'name':name}

def delete(token, topic_id):
    auth.authorise_user(token)


    for topic in database.topics:
        if topic.topic_id == topic_id:

            if topic.modules:
                raise DependencyError('This topic is being used by courses. To delete it, you have to remove it from all courses.')
            if topic.taskgroups:
                raise DependencyError('Topic must be empty to delete (no taskgroups).')

            database.topics.remove(topic)
            break

    database.update()

def edit(token, topic_id, name):
    auth.authorise_user(token)

    for topic in database.topics:
        if topic.topic_id == topic_id:
            topic.name = name
            topic.modified = time()

    database.update()
    return {'topic_id':topic_id, 'name':name}

def details(token, topic_id):
    auth.authorise_user(token)

    topic_details = Topic.select().where(Topic.id == topic_id).dicts().get()

    topic_details['taskgroups'] = taskgroups.listall(topic_id, topic.taskgroups)

    courses = []
    '''
    for module in database.modules:
        if module.topic == topic.topic_id:
            for course in database.courses:
                if course.course_id == module.course:
                    courses.append({'course_id': module.course, 'name': course.name})
                    break
    '''
    topic_details['courses'] = courses

    return {'topic': topic_details, 'currentTime': time()}
