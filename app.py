import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS

from data_store import database
import auth
import users
import courses
import topics
import taskgroups
import tasks
import attachments
import classes
import submissions

app = Flask(__name__)
CORS(app)

def default_handler(err):

    response = err.get_response()
    response.data = dumps({
        'code': err.code,
        'name': 'System Error',
        'message': err.get_description(),
    })
    response.content_type = 'application/json'

    return response

@app.route('/auth/login', methods=['POST'])
def login():
    payload = request.json
    username = payload['username']
    password = payload['password']
    print(username, password)

    return dumps(auth.login(username, password))

@app.route('/auth/logout', methods=['POST'])
def logout():
    payload = request.json
    token = payload['token']

    return dumps(auth.logout(token))

@app.route('/users/teachers/other', methods=['GET'])
def teachers_other():
    token = request.args.get('token')
    class_id = int(request.args.get('class_id'))

    return dumps(users.other_teachers(token, class_id))

@app.route('/users/students/other', methods=['GET'])
def students_other():
    token = request.args.get('token')
    class_id = int(request.args.get('class_id'))

    return dumps(users.other_students(token, class_id))

@app.route('/users/listall', methods=['GET'])
def students_listall():
    token = request.args.get('token')

    return dumps(users.listall(token))

@app.route('/users/delete', methods=['DELETE'])
def students_delete():
    payload = request.json
    token = payload['token']
    username = payload['username']

    users.delete(token, username)

    return dumps({})

@app.route('/users/import', methods=['POST'])
def users_import():
    payload = request.form
    token = payload['token']
    user_type = payload['type']
    file = request.files['file'] if request.files.get('file') else None

    if file is None:
        raise Exception

    return dumps(users.import_users(token, user_type, file))

@app.route('/user/password', methods=['PUT'])
def user_password():
    payload = request.json
    token = payload['token']
    old = payload['old_password']
    new = payload['new_password']
    confirm = payload['confirm_password']

    return dumps(users.update_password(token, old, new, confirm))

@app.route('/classes/teacher', methods=['GET'])
def classes_teacher():
    token = request.args.get('token')

    return dumps(classes.teacher_classes(token))

@app.route('/classes/student', methods=['GET'])
def classes_student():
    token = request.args.get('token')

    return dumps(classes.student_classes(token))

@app.route('/topics/list', methods=['GET'])
def topics_list():
    token = request.args.get('token')

    return dumps(topics.listall(token))

@app.route('/topics/add', methods=['POST'])
def topics_add():
    payload = request.json
    token = payload['token']
    name = payload['name']

    return dumps(topics.add(token, name))

@app.route('/topics/edit', methods=['PUT'])
def topics_edit():
    payload = request.json
    token = payload['token']
    topic_id = int(payload['topic_id'])
    name = payload['name']

    return dumps(topics.edit(token, topic_id, name))

@app.route('/topics/delete', methods=['DELETE'])
def topics_delete():
    payload = request.json
    token = payload['token']
    topic_id = int(payload['topic_id'])

    topics.delete(token, topic_id)

    return dumps({})

@app.route('/topics/details', methods=['GET'])
def topic_details():
    token = request.args.get('token')
    topic_id = int(request.args.get('topic_id'))
    return dumps(topics.details(token, topic_id))

@app.route('/taskgroups/add', methods=['POST'])
def taskgroups_add():
    payload = request.json
    token = payload['token']
    name = payload['name']
    submit_multiple = payload['submit_multiple']
    topic_id = int(payload['topic_id'])

    return dumps(taskgroups.add(token, topic_id, name, submit_multiple))

@app.route('/taskgroups/edit', methods=['PUT'])
def taskgroups_edit():
    payload = request.json
    token = payload['token']
    taskgroup_id = int(payload['taskgroup_id'])
    name = payload['name']

    return dumps(taskgroups.edit(token, taskgroup_id, name))

@app.route('/taskgroups/delete', methods=['DELETE'])
def taskgroups_delete():
    payload = request.json
    token = payload['token']
    taskgroup_id = int(payload['taskgroup_id'])

    taskgroups.delete(token, taskgroup_id)

    return dumps({})

@app.route('/taskgroups/reorder', methods=['PUT'])
def taskgroups_reorder():
    payload = request.json
    token = payload['token']
    topic_id = payload['topic_id']
    new_order = [int(i) for i in payload['newTaskGroupList']]

    return dumps(taskgroups.reorder(token, topic_id, new_order))

@app.route('/taskgroups/move', methods=['PUT'])
def taskgroups_move():
    payload = request.json
    token = payload['token']
    taskgroup_id = int(payload['taskgroup_id'])
    new_topic_id = int(payload['newTopic'])

    return dumps(taskgroups.move(token, taskgroup_id, new_topic_id))

@app.route('/taskgroups/details', methods=['GET'])
def taskgroups_details():
    token = request.args.get('token')
    taskgroup_id = int(request.args.get('taskgroup_id'))

    return dumps(taskgroups.details(token, taskgroup_id))

@app.route('/tasks/add', methods=['POST'])
def tasks_add():
    payload = request.json
    token = payload['token']
    taskgroup_id = int(payload['taskgroup_id'])
    name = payload['name']
    difficulty = payload['difficulty']
    type = payload['type']
    description = payload['description']
    hint = payload['hint']
    solution = payload['solution']

    return dumps(tasks.add(token, taskgroup_id, name, difficulty, type, description, hint, solution))

@app.route('/tasks/details', methods=['GET'])
def tasks_details():
    token = request.args.get('token')
    task_id = int(request.args.get('task_id'))

    return dumps(tasks.details(token, task_id))

@app.route('/tasks/edit', methods=['PUT'])
def tasks_edit():
    payload = request.json
    token = payload['token']
    task_id = int(payload['task_id'])
    name = payload['name']
    difficulty = payload['difficulty']
    description = payload['description']
    hint = payload['hint']
    solution = payload['solution']
    choices = payload['choices']
    correct_answers = payload['correct_answers']

    return dumps(tasks.edit(token, task_id, name, difficulty, description, hint, solution, choices, correct_answers))

@app.route('/tasks/delete', methods=['DELETE'])
def tasks_delete():
    payload = request.json
    token = payload['token']
    task_id = int(payload['task_id'])

    tasks.delete(token, task_id)

    return dumps({})

@app.route('/tasks/reorder', methods=['PUT'])
def tasks_reorder():
    payload = request.json
    token = payload['token']
    taskgroup_id = int(payload['taskgroup_id'])
    new_tasks = [int(i) for i in payload['newTaskList']]
    print(taskgroup_id, new_tasks)

    return dumps(tasks.reorder(token, taskgroup_id, new_tasks))

@app.route('/tasks/move', methods=['PUT'])
def tasks_move():
    payload = request.json
    token = payload['token']
    task_id = int(payload['task_id'])
    new_taskgroup_id = int(payload['newTaskgroup'])

    return dumps(tasks.move(token, task_id, new_taskgroup_id))

@app.route('/tasks/attachments', methods=['GET'])
def attachments_list():
    token = request.args.get('token')
    task_id = int(request.args.get('task_id'))

    return dumps(attachments.listall(token, task_id))

@app.route('/tasks/attachments/retrieve', methods=['GET'])
def attachments_retrieve():
    attachment_id = int(request.args.get('attachment_id'))

    return attachments.retrieve(attachment_id)

@app.route('/tasks/attachments/add', methods=['POST'])
def attachments_add():
    payload = request.form
    token = payload['token']
    task_id = int(payload['task_id'])
    cover_name = payload['cover_name']
    attachment = request.files['attachment'] if request.files.get('attachment') else None
    if attachment is None:
        raise Exception
    return dumps(attachments.add(token, task_id, cover_name, attachment))

@app.route('/tasks/attachments/delete', methods=['DELETE'])
def attachments_delete():
    payload = request.json
    token = payload['token']
    attachment_id = payload['attachment_id']

    attachments.delete(token, attachment_id)

    return dumps({})

@app.route('/courses/list', methods=['GET'])
def courses_list():
    token = request.args.get('token')

    return dumps(courses.listall(token))

@app.route('/courses/add', methods=['POST'])
def courses_add():
    payload = request.json
    token = payload['token']
    name = payload['name']

    return dumps(courses.add(token, name))

@app.route('/courses/edit', methods=['PUT'])
def courses_edit():
    payload = request.json
    token = payload['token']
    course_id = payload['course_id']
    name = payload['name']

    return dumps(courses.edit(token, course_id, name))

@app.route('/courses/delete', methods=['DELETE'])
def courses_delete():
    payload = request.json
    token = payload['token']
    course_id = payload['course_id']

    courses.delete(token, course_id)

    return dumps({})

@app.route('/courses/details', methods=['GET'])
def courses_details():
    token = request.args.get('token')
    course_id = int(request.args.get('course_id'))

    return dumps(courses.details(token, course_id))

@app.route('/courses/details/class', methods=['GET'])
def courses_details_class():
    token = request.args.get('token')
    course_id = int(request.args.get('course_id'))
    class_id = int(request.args.get('class_id'))

    return dumps(courses.details(token, course_id, class_id))

@app.route('/courses/topics/add', methods=['POST'])
def courses_topics_add():
    payload = request.json
    token = payload['token']
    course_id = int(payload['course_id'])
    topic_id = int(payload['topic_id'])
    name = payload['name']

    return dumps(courses.add_topic(token, course_id, topic_id, name))

@app.route('/courses/topics/rename', methods=['PUT'])
def courses_topics_rename():
    payload = request.json
    token = payload['token']
    module_id = int(payload['module_id'])
    name = payload['name']

    return dumps(courses.rename_topic(token, module_id, name))

@app.route('/courses/topics/remove', methods=['DELETE'])
def courses_topics_remove():
    payload = request.json
    token = payload['token']
    module_id = int(payload['module_id'])

    return dumps(courses.remove_topic(token, module_id))

@app.route('/courses/topics/reorder', methods=['PUT'])
def courses_topics_reorder():
    payload = request.json
    token = payload['token']
    course_id = int(payload['course_id'])
    new_topics_order = [int(i) for i in payload['newTopicList']]

    return dumps(courses.reorder_topics(token, course_id, new_topics_order))

@app.route('/classes/list', methods=['GET'])
def classes_list():
    token = request.args.get('token')

    return dumps(classes.listall(token))

@app.route('/classes/add', methods=['POST'])
def classes_add():
    payload = request.json
    token = payload['token']
    name = payload['name']
    year = payload['year']
    course = int(payload['course'])

    return dumps(classes.add(token, name, course, year))

@app.route('/classes/edit', methods=['PUT'])
def classes_edit():
    payload = request.json
    token = payload['token']
    class_id = int(payload['class_id'])
    name = payload['name']
    year = payload['year']
    teachers = payload['teachers']

    return dumps(classes.edit(token, class_id, name, year, teachers))

@app.route('/classes/delete', methods=['DELETE'])
def classes_delete():
    payload = request.json
    token = payload['token']
    class_id = int(payload['class_id'])

    classes.delete(token, class_id)

    return dumps({})

@app.route('/classes/details', methods=['GET'])
def classes_details():
    token = request.args.get('token')
    class_id = int(request.args.get('class_id'))

    return dumps(classes.details(token, class_id))

@app.route('/classes/topic/details', methods=['GET'])
def classes_topic_details():
    token = request.args.get('token')
    class_id = int(request.args.get('class_id'))
    topic_id = int(request.args.get('topic_id'))

    return dumps(classes.topic_details(token, class_id, topic_id))

@app.route('/classes/taskgroup/details', methods=['GET'])
def classes_taskgroup_details():
    token = request.args.get('token')
    class_id = int(request.args.get('class_id'))
    taskgroup_id = int(request.args.get('taskgroup_id'))

    return dumps(classes.taskgroup_details(token, class_id, taskgroup_id))

@app.route('/classes/enrolments/add', methods=['POST'])
def enrolments_add():
    payload = request.json
    token = payload['token']
    class_id = int(payload['class_id'])
    username = payload['username']

    return dumps(classes.add_enrolment(token, class_id, username))

@app.route('/classes/enrolments/remove', methods=['DELETE'])
def enrolments_remove():
    payload = request.json
    token = payload['token']
    class_id = int(payload['class_id'])
    username = payload['username']
    classes.remove_enrolment(token, class_id, username)

    return dumps({})

@app.route('/classes/enrolments/import', methods=['POST'])
def enrolments_import():
    payload = request.form
    token = payload['token']
    class_id = int(payload['class_id'])
    file = request.files['file'] if request.files.get('file') else None

    if file is None:
        raise Exception

    return dumps(classes.import_enrolments(token, class_id, file))

@app.route('/courses/submissions', methods=['GET'])
def submissions_list():
    token = request.args.get('token')
    course_id = int(request.args.get('course_id'))

    return dumps(submissions.listall(token, course_id))

@app.route('/courses/submissions/student', methods=['GET'])
def submissions_list_student():
    token = request.args.get('token')
    course_id = int(request.args.get('course_id'))
    student_id = request.args.get('student_id')

    return dumps(submissions.listall(token, course_id, student_id))

@app.route('/submissions/details', methods=['GET'])
def tasks_submissions():
    token = request.args.get('token')
    submission_id = int(request.args.get('submission_id'))

    return dumps(submissions.details(token, submission_id))

@app.route('/tasks/submit', methods=['POST'])
def submit():
    payload = request.form
    token = payload['token']
    tasks = [int(i) for i in payload['tasks'].split(',')]
    files = []
    selected_answer = payload.get('selected_answer')
    print(selected_answer)

    if selected_answer != None:
        try:
            return dumps(submissions.submit(token, tasks, selected_answer=list(map(int, selected_answer.split(',')))))
        except:
            print('does this twork?')
            return dumps(submissions.submit(token, tasks, selected_answer=selected_answer))

    fileNum = 0
    while request.files.get(f'file{fileNum}') != None:
        files.append(request.files[f'file{fileNum}'])
        fileNum += 1

    return dumps(submissions.submit(token, tasks, files))

@app.route('/tasks/submissions/retrieve', methods=['GET'])
def retrieve_submission():
    submission_id = int(request.args.get('submission_id'))
    file_num = int(request.args.get('filenum'))

    return submissions.retrieve(submission_id, file_num)

@app.route('/submissions/mark', methods=['PUT'])
def mark_submission():
    payload = request.json
    token = payload['token']
    submission_id = int(payload['submission_id'])
    status = payload['status']

    return dumps(submissions.mark(token, submission_id, status))

@app.route('/submissions/comment', methods=['POST'])
def comment_submission():
    payload = request.json
    token = payload['token']
    submission_id = int(payload['submission_id'])
    comment = payload['comment']

    return dumps(submissions.add_comment(token, submission_id, comment))

app.config['TRAP_HTTP_EXCEPTIONS'] = True
app.register_error_handler(Exception, default_handler)

if __name__ == '__main__':
    database.read()
    print('Starting....')
    print(database.users)
    # print(database.active_tokens)
    app.run(port=5000)
