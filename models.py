import os

from urllib.parse import urlparse
from peewee import PostgresqlDatabase, SqliteDatabase, Model, TextField, ForeignKeyField, DateTimeField, BooleanField, IntegerField

if 'HEROKU' in os.environ:
    url = urlparse(os.environ['DATABASE_URL'])
    db = PostgresqlDatabase(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port
    )
else:
    db = SqliteDatabase(
        'test.db',
        pragmas={
            'foreign_keys': 'on'
        }
    )

class OsirisEntity(Model):
    class Meta:
        database = db

class User(OsirisEntity):
    username = TextField()
    password = TextField()
    user_type = TextField()
    name = TextField()

class Course(OsirisEntity):
    name = TextField()
    modified = DateTimeField()

class Class(OsirisEntity):
    name = TextField()
    course = ForeignKeyField(Course)
    year = IntegerField()

class Enrolment(OsirisEntity):
    user = ForeignKeyField(User)
    cls = ForeignKeyField(Class)

class Topic(OsirisEntity):
    name = TextField()
    modified = DateTimeField()

class Module(OsirisEntity):
    name = TextField()
    topic = ForeignKeyField(Topic)
    course = ForeignKeyField(Course)

class Taskgroup(OsirisEntity):
    topic = ForeignKeyField(Topic)
    name = TextField()
    modified = DateTimeField()
    submit_multiple = BooleanField()

class Choice(OsirisEntity):
    content = TextField()

class Task(OsirisEntity):
    taskgroup = ForeignKeyField(Taskgroup)
    name = TextField()
    difficulty = TextField() # change to enum
    answer_type = TextField() # change to enum
    description = TextField()
    hint = TextField()
    solution = TextField()
    modified = DateTimeField()
    correct_answer = ForeignKeyField(Choice, null=True)

class Attachment(OsirisEntity):
    task = ForeignKeyField(Task)
    cover_name = TextField()
    storage_name = TextField()

class Submission(OsirisEntity):
    student = ForeignKeyField(User)
    comment = TextField()
    status = TextField() # change to enum
    selected_answer = ForeignKeyField(Choice, null=True)
    time = DateTimeField()

class TaskSubmission(OsirisEntity):
    task = ForeignKeyField(Task)
    submission = ForeignKeyField(Submission)

class File(OsirisEntity):
    submission = ForeignKeyField(Submission)
    format = TextField()
    cover_name = TextField()

class ActiveToken(OsirisEntity):
    user = ForeignKeyField(User)
    token = TextField()

def main():
    db.connect()
    db.create_tables([User, Enrolment, Course, Class, Topic, Module, Taskgroup, Task, Choice, Attachment, Submission, TaskSubmission, File, ActiveToken])
    db.close()
