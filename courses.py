from time import time
from data_store import database, Course, Module
from error import InputError, AccessError, DependencyError
import taskgroups

def add(token, name):
    auth.authorise_user(token)

    course_id = database.generate_id('course')
    new_course = Course(course_id, name)

    database.courses.append(new_course)

    database.update()

    return new_course.json()

def edit(token, course_id, name):
    auth.authorise_user(token)

    for course in database.courses:
        if course.course_id == course_id:
            course.name = name
            course.modified = time()

            database.update()

            return {'course': course.json()}

def delete(token, course_id):
    auth.authorise_user(token)

    for course in database.courses:
        if course.course_id == course_id:
            print(course.modules)
            if course.modules:
                raise DependencyError('You need to remove all topics from a course before deleting a course')
            elif course.classes:
                raise DependencyError('Classes which use this course need to be deleted before deleting a class')
            else:
                database.courses.remove(course)
                break

    database.update()

def listall(token):
    return {'courses': [course.json() for course in database.courses], 'currentTime': time()}

def details(token, course_id, class_id=None):
    auth.authorise_user(token)

    for course in database.courses:
        if course.course_id == course_id:
            course_details = course.json()
            modules = []

            for module in database.modules:
                if module.course == course_id:
                    for topic in database.topics:
                        if topic.topic_id == module.topic:
                            modules.append({'topic_name': topic.name,
                                           'module_name': module.name,
                                           'topic_id': topic.topic_id,
                                           'module_id': module.module_id,
                                           'taskgroups': taskgroups.listall(topic.topic_id, topic.taskgroups) })

            modules.sort(key=lambda md: course.modules.index(md['module_id']))
            course_details['modules'] = modules

            if class_id is None:
                course_details['classes'] = []
                for c in database.classes:
                    if c.class_id in course.classes:
                        course_details['classes'].append({'class_id': c.class_id, 'name': c.name})
            else:
                for c in database.classes:
                    if c.class_id == class_id:
                        course_details['classname'] = c.name

            return {'course': course_details}

def add_topic(token, course_id, topic_id, name):
    auth.authorise_user(token)

    module_id = database.generate_id('module')
    new_module = Module(module_id, topic_id, course_id, name)

    database.modules.append(new_module)

    for course in database.courses:
        if course.course_id == course_id:
            course.modules.append(module_id)

    for topic in database.topics:
        if topic.topic_id == topic_id:
            topic.modules.append(module_id)

    database.update()

    return {'module': new_module.json()}

def rename_topic(token, module_id, name):
    auth.authorise_user(token)

    for module in database.modules:
        if module.module_id == module_id:
            module.name = name

            database.update()

            return {'module': module.json()}

def remove_topic(token, module_id):
    auth.authorise_user(token)

    for module in database.modules:
        if module.module_id == module_id:
            database.modules.remove(module)

    for topic in database.topics:
        if module_id in topic.modules:
            topic.modules.remove(module_id)

    for course in database.courses:
        if module_id in course.modules:
            course.modules.remove(module_id)

    database.update()

def reorder_topics(token, course_id, new_modules):
    for course in database.courses:
        if course.course_id == course_id:
            course.modules = new_modules
            course.modified = time()

    database.update()

    return {}
