from time import time
from data_store import database, Topic
from error import InputError, AccessError, DependencyError
import taskgroups

def listall(token):
    database.authorise_user(token)

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

    return {'topics': topics, 'currentTime': time()}

def add(token, name):
    database.authorise_user(token)

    topic_id = database.generate_id('topic')

    new_topic = Topic(topic_id, name)
    database.topics.append(new_topic)

    database.update()
    return {'topic_id':topic_id, 'name':name}

def delete(token, topic_id):
    database.authorise_user(token)


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
    database.authorise_user(token)

    for topic in database.topics:
        if topic.topic_id == topic_id:
            topic.name = name
            topic.modified = time()

    database.update()
    return {'topic_id':topic_id, 'name':name}

def details(token, topic_id):
    database.authorise_user(token)

    for topic in database.topics:
        if topic.topic_id == topic_id:
            topic_details = topic.json()

            topic_details['taskgroups'] = taskgroups.listall(topic_id, topic.taskgroups)

            courses = []
            for module in database.modules:
                if module.topic == topic.topic_id:
                    for course in database.courses:
                        if course.course_id == module.course:
                            courses.append({'course_id': module.course, 'name': course.name})
                            break

            topic_details['courses'] = courses

            return {'topic': topic_details, 'currentTime': time()}
