import csv
from io import StringIO
from data_store import database, Class
from error import InputError, AccessError, DependencyError
import submissions
import auth
from models import User

def add(token, name, course_id, year):
    auth.authorise_user(token)

    teacher = database.active_tokens[token]

    class_id = database.generate_id('class')

    new_class = Class(class_id, name, course_id, year, [teacher])
    database.classes.append(new_class)

    for course in database.courses:
        if course.course_id == course_id:
            course.classes.append(class_id)

    for user in database.users:
        if user.username == teacher:
            user.classes.append(class_id)

    database.update()
    return new_class.json()

def edit(token, class_id, name, year, teachers):
    auth.authorise_user(token)

    for c in database.classes:
        if c.class_id == class_id:
            c.name = name
            c.year = year
            c.teachers = teachers

            for user in database.users:
                print(user.username, user.classes, teachers)
                if user.username in teachers and class_id not in user.classes:
                    user.classes.append(class_id)
                elif user.username not in teachers and class_id in user.classes and user.user_type == 'teacher':
                    user.classes.remove(class_id)

            break

    database.update()
    return c.json()

def delete(token, class_id):
    auth.authorise_user(token)

    for c in database.classes:
        if c.class_id == class_id:

            if c.students:
                raise DependencyError('All students must be removed before deleting a class')

            for course in database.courses:
                if class_id in course.classes:
                    course.classes.remove(class_id)

            database.classes.remove(c)
            break

    database.update()

def details(token, class_id):
    auth.authorise_user(token)

    for c in database.classes:
        if c.class_id == class_id:
            class_details = c.json()

            for course in database.courses:
                if course.course_id == c.course:
                    topics = []

                    for module in database.modules:
                        if module.course == course.course_id:
                            topics.append({'topic_id':module.topic, 'name':module.name})

                    class_details['course'] = {'course_id': course.course_id, 'name': course.name, 'topics':topics}
                    break

            class_details['teachers'] = []
            class_details['students'] = []
            for user in database.users:
                if user.username in c.teachers:
                    class_details['teachers'].append({'name':user.name, 'username':user.username})
                elif user.username in c.students:
                    class_details['students'].append({'name':user.name, 'username':user.username,
                                                     'progress': submissions.topics_progress(c.course, user.username),
                                                     'difficulty': {
                                                        'course': submissions.course_difficulty(c.course, user.username),
                                                        'topics': submissions.topics_difficulty(c.course, user.username)
                                                     }
                                                    })

            return {'class': class_details}
    else:
        raise InputError('Class id is invalid.')

def topic_details(token, class_id, topic_id):
    auth.authorise_user(token)

    for c in database.classes:
        if c.class_id == class_id:
            class_details = c.json()

            for course in database.courses:
                if course.course_id == c.course:
                    class_details['course'] = {'course_id':c.course, 'name': course.name}
                    break

            class_details['teachers'] = []
            class_details['students'] = []
            for user in database.users:
                if user.username in c.teachers:
                    class_details['teachers'].append({'name':user.name, 'username':user.username})
                elif user.username in c.students:
                    class_details['students'].append({'name':user.name, 'username':user.username,
                                                     'progress': submissions.taskgroups_progress(topic_id, user.username)})

            return {'class': class_details}

def taskgroup_details(token, class_id, taskgroup_id):
    auth.authorise_user(token)

    for c in database.classes:
        if c.class_id == class_id:
            class_details = c.json()

            for course in database.courses:
                if course.course_id == c.course:
                    class_details['course'] = {'course_id':c.course, 'name': course.name}
                    break

            class_details['teachers'] = []
            class_details['students'] = []
            for user in database.users:
                if user.username in c.teachers:
                    class_details['teachers'].append({'name':user.name, 'username':user.username})
                elif user.username in c.students:
                    class_details['students'].append({'name':user.name, 'username':user.username,
                                                     'progress': submissions.tasks_progress(taskgroup_id, user.username)})

            return {'class': class_details}

def listall(token):
    classes = []

    for c in database.classes:
        class_details = c.json()
        for course in database.courses:
            if course.course_id == c.course:
                class_details['course'] = {'course_id':c.course, 'name': course.name}
                break

        class_details['teachers'] = []
        for user in database.users:
            if user.username in c.teachers:
                class_details['teachers'].append(user.name)

        classes.append(class_details)

    return {'classes': classes}

def add_enrolment(token, class_id, student_id):
    auth.authorise_user(token)

    print(database.classes)
    for c in database.classes:
        if c.class_id == class_id:

            if student_id in c.students:
                raise InputError('Student is already enrolled in this class')

            c.students.append(student_id)

            for user in database.users:
                print(user.username, student_id, user.username == student_id)
                if user.username == student_id:
                    user.classes.append(class_id)
                    break
            break

    database.update()

    return {}

def import_enrolments(token, class_id, file):
    auth.authorise_user(token)

    if not file.filename.endswith('.csv'):
        raise InputError('Values must be a .csv file.')

    FILE = StringIO(file.read().decode('utf-8'))
    print(FILE)
    reader = csv.reader(FILE)

    for row in reader:
        username = ''.join([char for char in row[0] if char.isalpha() or char.isnumeric()])
        print(username)
        add_enrolment(token, class_id, username)

    return {}

def remove_enrolment(token, class_id, student_id):
    auth.authorise_user(token)

    for c in database.classes:
        if c.class_id == class_id:
            c.students.remove(student_id)

            for user in database.users:
                if user.username == student_id:
                    user.classes.remove(class_id)
                    break
            break

    database.update()

def teacher_classes(token):
    teacher_id = auth.authorise_user(token)
    print(teacher_id)

    classes = []
    '''
    for c in database.classes:
        print(c.teachers, teacher_id)
        if teacher_id in c.teachers:
            classes.append({'class_id':c.class_id, 'name': c.name, 'submissions': submissions.recent_submissions(c.class_id)})
    '''
    user = User.select().where(User.id == teacher_id).get()

    return {'classes': classes, 'name': user.name}

def student_classes(token):
    auth.authorise_user(token)
    student_id = database.active_tokens[token]

    classes = []
    for c in database.classes:
        if student_id in c.students:
            class_details = details(token, c.class_id)['class']
            class_details['progress'] = {'course': submissions.course_progress(c.course, student_id),
                                         'topics': submissions.topics_progress(c.course, student_id)}

            classes.append(class_details)

    return {'classes': classes}
