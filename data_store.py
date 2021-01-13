from json import dumps, loads
import time
from error import InputError, AccessError

class Data_Store(object):
    def __init__(self):
        self.active_tokens = {}
        self.users = []
        self.courses = []
        self.topics = []
        self.taskgroups = []
        self.attachments = []
        self.submissions = []
        self.classes = []
        self.next_id = {}

    def authenticate_user(self, username, hashed_password):
        print(self.users)
        for user in self.users:
            if user.username == username and user.password == hashed_password:
                return user.user_type
        return False

    def authorise_user(self, token):
        print(self.active_tokens)
        print(token in self.active_tokens)
        if token not in self.active_tokens:
            raise AccessError('Unauthorised User')

    def read(self):
        f = open('data_store.json')
        with open('data_store.json', 'r') as FILE:
            data = loads(FILE.read())
            print(data)

            for item in data['users']:
                self.users.append(User(item['username'], item['password'], item['user_type'], item['name'], item['classes']))

            self.courses = [Course(item['course_id'], item['name'], item['modules'], item['classes'], item['modified']) for item in data['courses']]
            self.modules = [Module(item['module_id'], item['topic'], item['course'], item['name']) for item in data['modules']]
            self.topics = [Topic(item['topic_id'], item['name'], item['taskgroups'], item['modules'], item['modified']) for item in data['topics']]
            self.taskgroups = [Taskgroup(item['taskgroup_id'],
                              item['topic_id'],
                              item['name'], item['submit_multiple'], item['tasks'], item['modified']) for item in data['taskgroups']]
            self.tasks = [Task(item['task_id'], item['taskgroup_id'], item['name'],
                                item['difficulty'], item['answer_type'], item['description'],
                                item['hint'], item['solution'], item['attachments'], item['modified'], item['choices'], item['correct_answer']) for item in data['tasks']]
            self.attachments = [Attachment(item['attachment_id'], item['task_id'], item['cover_name'], item['storage_name']) for item in data['attachments']]
            self.classes = [Class(item['class_id'], item['name'], item['course'], item['year'], item['teachers'], item['students']) for item in data['classes']]
            self.submissions = [Submission(item['submission_id'], item['tasks'], item['student'], item['time'], item['comment'], item['status'], files=item['files'], selected_answer=['selected_answer']) for item in data['submissions']]

            self.active_tokens = data['active_tokens']
            print('Active tokens have been reset')
            self.next_id = data['next_id']

    def update(self):
        with open('data_store.json', 'w') as FILE:
            data = dumps({'users': [user.json() for user in self.users],
                          'courses': [course.json() for course in self.courses],
                          'topics': [topic.json() for topic in self.topics],
                          'modules': [module.json() for module in self.modules],
                          'taskgroups': [taskgroup.json() for taskgroup in self.taskgroups],
                          'tasks': [task.json() for task in self.tasks],
                          'attachments': [attachment.json() for attachment in self.attachments],
                          'classes': [c.json() for c in self.classes],
                          'submissions': [submission.json() for submission in self.submissions],
                          'next_id': self.next_id,
                          'active_tokens': self.active_tokens
            })
            FILE.write(data)

    def get_user(username):
        for user in self.users:
            if user.username == username:
                return user

        raise ValueError('Username given was invalid')

    def generate_id(self, object_type):
        result = 1

        if object_type in self.next_id:
            result = self.next_id[object_type]
            self.next_id[object_type] += 1
        else:
            self.next_id[object_type] = 2

        return result


class User(object):
    def __init__(self, username, password, user_type, name, classes=[]):
        self.username = username
        self.password = password
        self.user_type = user_type
        self.classes = classes
        self.name = name

    def json(self):
        return {'username':self.username, 'password':self.password,
        'user_type': self.user_type, 'classes': self.classes, 'name':self.name}

class Topic(object):
    def __init__(self, topic_id, name, taskgroups=[], modules=[], modified=None):
        self.topic_id = topic_id
        self.name = name
        self.taskgroups = taskgroups
        self.modules = modules
        self.modified = modified if modified is not None else time.time()

    def json(self):
        return {'topic_id':self.topic_id, 'name':self.name, 'modified': self.modified,
                'taskgroups': self.taskgroups, 'modules': self.modules}

class Taskgroup(object):
    def __init__(self, taskgroup_id, topic_id, name, submit_multiple, tasks=[], modified=None):
        self.taskgroup_id = taskgroup_id
        self.topic_id = topic_id
        self.name = name
        self.tasks = tasks
        self.modified = modified if modified is not None else time.time()
        self.submit_multiple = submit_multiple

    def json(self):
        return {'taskgroup_id':self.taskgroup_id, 'topic_id':self.topic_id, 'name': self.name,
                'tasks': self.tasks, 'modified': self.modified, 'submit_multiple': self.submit_multiple }

class Task(object):
    def __init__(self, task_id, taskgroup_id, name, difficulty, type, description, hint, solution, attachments=[], modified=None, choices=[], correct_answer=None):
        self.task_id = task_id
        self.taskgroup_id = taskgroup_id
        self.name = name
        self.difficulty = difficulty
        self.answer_type = type
        self.description = description
        self.hint = hint
        self.solution = solution
        self.attachments = attachments
        self.modified = modified if modified is not None else time.time()
        self.choices = choices
        self.correct_answer = correct_answer

    def json(self):
        return {'task_id':self.task_id, 'taskgroup_id':self.taskgroup_id, 'name':self.name, 'difficulty': self.difficulty, 'answer_type': self.answer_type,
                'description':self.description, 'hint':self.hint, 'solution':self.solution, 'attachments': self.attachments, 'modified': self.modified, 'choices': self.choices,
                'correct_answer': self.correct_answer }

class Course(object):
    def __init__(self, course_id, name, modules=[], classes=[], modified=None):
        self.course_id = course_id
        self.name = name
        self.modules = modules
        self.classes = classes
        self.modified = modified if modified is not None else time.time()

    def json(self):
        return {'course_id':self.course_id, 'name': self.name,
                'modules': self.modules, 'classes': self.classes, 'modified': self.modified }

class Module(object):
    def __init__(self, module_id, topic_id, course_id, name):
        self.module_id = module_id
        self.topic = topic_id
        self.course = course_id
        self.name = name

    def json(self):
        return {'module_id': self.module_id, 'topic': self.topic, 'course': self.course, 'name': self.name}

class Attachment(object):
    def __init__(self, attachment_id, task_id, cover_name, storage_name):
        self.attachment_id = attachment_id
        self.cover_name = cover_name
        self.task_id = task_id
        self.storage_name = storage_name

    def json(self):
        return {'attachment_id':self.attachment_id, 'cover_name': self.cover_name,
        'storage_name': self.storage_name, 'task_id':self.task_id }

class Class(object):
    def __init__(self, class_id, name, course, year, teachers=[], students=[]):
        self.class_id = class_id
        self.name = name
        self.course = course
        self.year = year
        self.teachers = teachers
        self.students = students

    def json(self):
        return {'class_id':self.class_id, 'course':self.course,
                'name': self.name, 'year':self.year,
                'teachers':self.teachers, 'students':self.students}

class Submission(object):
    def __init__(self, submission_id, tasks, student, timestamp=None, comment='', status='unmarked', files=[], files_raw=[], selected_answer=-1):
        self.submission_id = submission_id
        self.tasks = tasks
        self.student = student
        self.comment = comment
        self.time = timestamp if timestamp is not None else time.time()
        if not files_raw:
            self.files = [File(file['format'], file['cover_name'], file['submission_id'], file['file_no']) for file in files]
        else:
            self.files = files_raw
        self.status = status
        self.selected_answer = selected_answer

    def json(self):
        return {'submission_id': self.submission_id, 'tasks': self.tasks,
                'student': self.student, 'status': self.status,
                'time': self.time, 'comment':self.comment,
                'files': [file.json() for file in self.files],
                'selected_answer': self.selected_answer}


class File(object):
    def __init__(self, format, cover_name, submission_id, file_no):
        self.format = format
        self.cover_name = cover_name
        self.submission_id = submission_id
        self.file_no = file_no

    @property
    def filename_path(self):
        return f'{self.submission_id}.{self.file_no}.{self.format}'

    @property
    def filename_show(self):
        return f'{self.cover_name}.{self.format}'

    def json(self):
        return {'cover_name': self.cover_name, 'format': self.format, 'submission_id': self.submission_id, 'file_no': self.file_no}

global database
database = Data_Store()
