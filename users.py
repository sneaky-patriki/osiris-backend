import csv
from io import StringIO
from data_store import database, User
from error import DependencyError
import hashlib

def other_teachers(token, class_id):
    auth.authorise_user(token)

    for c in database.classes:
        if c.class_id == class_id:
            break

    return {'teachers': [user.json() for user in database.users \
            if user.user_type == 'teacher' and user.username not in c.teachers]}

def other_students(token, class_id):
    auth.authorise_user(token)

    for c in database.classes:
        if c.class_id == class_id:
            break

    return {'students': [user.json() for user in database.users \
            if user.user_type == 'student' and user.username not in c.students]}

def listall(token):
    auth.authorise_user(token)
    students = []
    teachers = []

    for user in database.users:
        cls = []
        if user.user_type == 'student':
            for c in database.classes:
                if user.username in c.students:
                    cls.append(c.name)

            student_data = user.json()
            student_data['classes'] = cls
            students.append(student_data)

        elif user.user_type == 'teacher':
            for c in database.classes:
                if user.username in c.teachers:
                    cls.append(c.name)

            teacher_data = user.json()
            teacher_data['classes'] = cls
            teachers.append(teacher_data)

    return {'students': students, 'teachers': teachers}

def delete(token, username):
    auth.authorise_user(token)

    if database.active_tokens[token] == username:
        raise DependencyError('You cannot delete yourself, nice try.')

    for c in database.classes:
        if username in c.students or username in c.teachers:
            raise DependencyError('User must be removed from all classes before being deleted.')

    for user in database.users:
        if user.username == username:
            database.users.remove(user)

            database.update()

def import_users(token, type, file):
    auth.authorise_user(token)

    if not file.filename.endswith('.csv'):
        raise InputError('Values must be a .csv file.')

    FILE = StringIO(file.read().decode('utf-8'))
    reader = csv.reader(FILE)

    for row in reader:
        username = ''.join([ char for char in row[0] if char.isalpha() or char.isnumeric()])
        name = ''.join([ char for char in row[1] if char.isalpha() or char.isnumeric() or char == ' '])
        new_user = User(validate_username(username), username + username, type, name)

        database.users.append(new_user)

    database.update()

    return {}

def validate_username(username):
    for user in database.users:
        if user.username == username:
            return validate_username(username + '1')
    return username

def update_password(token, old, new, confirm):
    auth.authorise_user(token)

    username = database.active_tokens[token]

    for user in database.users:
        if user.username == username:
            type = user.user_type

            encoder1 = hashlib.sha224()
            encoder1.update(old.encode('utf-8'))
            hashed_old = encoder1.hexdigest()

            if (hashed_old != user.password):
                raise InputError('Incorrect password given.')

            if (new != confirm):
                raise InputError('Passwords do not match.')

            encoder2 = hashlib.sha224()
            encoder2.update(new.encode('utf-8'))
            hashed_new = encoder2.hexdigest()

            user.password = hashed_new

            database.update()

            return {'type': type}
