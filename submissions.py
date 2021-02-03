import os
from time import time
from flask import send_from_directory
from data_store import database, Submission, File
from error import InputError

def submit(token, tasks, files=[], selected_answer=-1):
    auth.authorise_user(token)
    submission_id = database.generate_id('submission')
    student = database.active_tokens[token]

    if selected_answer == -1:
        file_store = []

        numFiles = 0
        for file in files:
            try:
                format = file.filename.split('.')[-1]
                filename = file.filename.split('.')[:-1]
            except IndexError:
                raise InputError('Invalid file format')

            new_file = File(format, file.filename, submission_id, numFiles)
            file_store.append(new_file)
            file.save(os.path.join('Submissions', new_file.filename_path))
            numFiles += 1

        print(files, numFiles)

        new_submission = Submission(submission_id, tasks, student, files_raw=file_store)
    else:
        for task in database.tasks:
            if task.task_id == tasks[0]:
                if task.answer_type == 'multiple-choice-single':
                    new_submission = Submission(submission_id, tasks, student, selected_answer=selected_answer[0])
                elif task.answer_type == 'multiple-choice-multiple' or task.answer_type == 'short-answer':
                    new_submission = Submission(submission_id, tasks, student, selected_answer=selected_answer)

    database.submissions.append(new_submission)
    database.update()
    return {'submission': new_submission.json()}

def course_tasks(course_id):
    topics = [module.topic for module in database.modules if module.course == course_id]
    taskgroups = []

    for topic in database.topics:
        if topic.topic_id in topics:
            taskgroups.extend(topic.taskgroups)

    tasks = []
    for taskgroup in database.taskgroups:
        if taskgroup.taskgroup_id in taskgroups:
            tasks.extend(taskgroup.tasks)

    return tasks

def listall(token, course_id, student_id=None):
    auth.authorise_user(token)

    if student_id is None:
        student_id = database.active_tokens[token]

    tasks = course_tasks(course_id)

    submissions = []
    for submission in database.submissions:
        for task in tasks:
            if task in submission.tasks and submission.student == student_id:
                submission_details = submission.json()
                submission_details['url'] = f'http://127.0.0.1:8080/tasks/submissions/retrieve?submission_id={submission.submission_id}'
                submission_details['currentTime'] = time()

                for file in range(len(submission.files)):
                    f = submission.files[file].json()
                    f['url'] = f'http://127.0.0.1:8080/tasks/submissions/retrieve?submission_id={submission.submission_id}&filenum={file}'
                    submission_details['files'][file] = f

                submissions.append(submission_details)

    for user in database.users:
        if user.username == student_id:
            name = user.name

    progress = topics_progress(course_id, student_id)
    return {'submissions': submissions, 'progress': progress, 'name': name}


def details(token, submission_id):
    auth.authorise_user(token)

    for submission in database.submissions:
        if submission.submission_id == submission_id:
            submission_details = submission.json()

            for task in database.tasks:
                if task.task_id == submission.tasks[-1]:
                    submission_details['task'] = task.json()

                    for file in range(len(submission.files)):
                        f = submission.files[file].json()
                        f['url'] = f'http://127.0.0.1:8080/tasks/submissions/retrieve?submission_id={submission.submission_id}&filenum={file}'
                        submission_details['files'][file] = f

                    return {'submission': submission_details}

def retrieve(submission_id, file_num):
    for submission in database.submissions:
        if submission.submission_id == submission_id:
            for file in submission.files:
                if file.file_no == file_num:
                    return send_from_directory('Submissions/', file.filename_path)

def course_progress(course_id, student_id):
    database.submissions.sort(key=lambda x : x.time, reverse=True)

    for course in database.courses:
        course_total = 0
        course_progress = {'unmarked':0, 'correct':0, 'incorrect':0}
        tasks_viewed = []

        if course.course_id == course_id:
            for module in database.modules:
                if module.course == course_id:
                    for taskgroup in database.taskgroups:
                        if taskgroup.topic_id == module.topic:
                            for task in database.tasks:
                                if task.taskgroup_id == taskgroup.taskgroup_id and task.answer_type != 'content':
                                    for submission in database.submissions:
                                        if task.task_id in submission.tasks and submission.student == student_id and task.task_id not in tasks_viewed:
                                            course_progress[submission.status] += 1
                                            tasks_viewed.append(task.task_id)
                                    course_total += 1

            if course_total > 0:

                summary = {
                    'unmarked': 100 * course_progress['unmarked'] / course_total,
                    'correct': 100 * course_progress['correct'] / course_total,
                    'incorrect': 100 * course_progress['incorrect'] / course_total
                }
            else:
                summary = {
                    'unmarked': 0,
                    'correct': 0,
                    'incorrect': 0
                }

            return summary

def course_difficulty(course_id, student_id):
    for course in database.courses:
        total_difficulty = {'Bronze':0, 'Silver':0, 'Gold':0, 'Platinum':0, 'Kryptonite':0, 'Unspecified': 0}
        difficulty_progress = {'Bronze':0, 'Silver':0, 'Gold':0, 'Platinum':0, 'Kryptonite':0, 'Unspecified': 0}

        if course.course_id == course_id:
            for module in database.modules:
                if module.course == course_id:
                    for taskgroup in database.taskgroups:
                        if taskgroup.topic_id == module.topic:
                            for task in database.tasks:
                                task_viewed = False
                                if task.taskgroup_id == taskgroup.taskgroup_id  and task.answer_type != 'content':
                                    for submission in database.submissions:
                                        if task.task_id in submission.tasks and submission.student == student_id and not task_viewed:
                                            difficulty_progress[task.difficulty] += 1
                                            task_viewed = True
                                    total_difficulty[task.difficulty] += 1

            summary = {}
            for difficulty in ['Bronze', 'Silver', 'Gold', 'Platinum', 'Kryptonite', 'Unspecified']:
                if total_difficulty[difficulty] > 0:
                    summary[difficulty] = 100 * difficulty_progress[difficulty] / total_difficulty[difficulty]
                else:
                    summary[difficulty] = None

            return summary

def topics_progress(course_id, student_id):
    database.submissions.sort(key=lambda x : x.time, reverse=True)

    for course in database.courses:
        if course_id == course.course_id:
            progress = []
            tasks_viewed = []

            for module in database.modules:
                if module.course == course_id:
                    topic_total = 0
                    topic_progress = {'unmarked':0, 'correct':0, 'incorrect':0}

                    for taskgroup in database.taskgroups:
                        if taskgroup.topic_id == module.topic:
                            for task in database.tasks:
                                if task.taskgroup_id == taskgroup.taskgroup_id and task.answer_type != 'content':
                                    for submission in database.submissions:
                                        if task.task_id in submission.tasks and submission.student == student_id and task.task_id not in tasks_viewed:
                                            topic_progress[submission.status] += 1
                                            tasks_viewed.append(task.task_id)
                                    topic_total += 1

                    if topic_total > 0:
                        if topic_progress['unmarked'] + topic_progress['correct'] > topic_total:
                            topic_progress['correct'] -= topic_progress['unmarked']
                        if topic_progress['unmarked'] + topic_progress['incorrect'] > topic_total:
                            topic_progress['incorrect'] -= topic_progress['unmarked']

                        if topic_progress['unmarked'] > topic_total:
                            topic_progress['unmarked'] = topic_total
                        elif topic_progress['correct'] > topic_total:
                            topic_progress['correct'] = topic_total
                        elif topic_progress['incorrect'] > topic_total:
                            topic_progress['incorrect'] = topic_total
                        print(topic_progress)

                        summary = {
                            'unmarked': 100 * topic_progress['unmarked'] / topic_total,
                            'correct': 100 * topic_progress['correct'] / topic_total,
                            'incorrect': 100 * topic_progress['incorrect'] / topic_total
                        }
                    else:
                        summary = {
                            'unmarked': 0,
                            'correct': 0,
                            'incorrect': 0
                        }

                    progress.append({'module':module.module_id, 'progress': summary})

            progress.sort(key=lambda pg: course.modules.index(pg['module']))
            return progress

def topics_difficulty(course_id, student_id):
    for course in database.courses:
        if course_id == course.course_id:
            progress = []

            for module in database.modules:
                if module.course == course_id:
                    total_difficulty = {'Bronze':0, 'Silver':0, 'Gold':0, 'Platinum':0, 'Kryptonite':0, 'Unspecified': 0}
                    difficulty_progress = {'Bronze':0, 'Silver':0, 'Gold':0, 'Platinum':0, 'Kryptonite':0, 'Unspecified': 0}

                    for taskgroup in database.taskgroups:
                        if taskgroup.topic_id == module.topic:
                            for task in database.tasks:
                                task_viewed = False
                                if task.taskgroup_id == taskgroup.taskgroup_id  and task.answer_type != 'content':
                                    for submission in database.submissions:
                                        if task.task_id in submission.tasks and submission.student == student_id and not task_viewed:
                                            difficulty_progress[task.difficulty] += 1
                                            task_viewed = True
                                    total_difficulty[task.difficulty] += 1

                    summary = {}
                    for difficulty in ['Bronze', 'Silver', 'Gold', 'Platinum', 'Kryptonite', 'Unspecified']:
                        if total_difficulty[difficulty] > 0:
                            summary[difficulty] = 100 * difficulty_progress[difficulty] / total_difficulty[difficulty]
                        else:
                            summary[difficulty] = None

                    progress.append({'module':module.module_id, 'progress': summary})

            progress.sort(key=lambda pg: course.modules.index(pg['module']))
            return progress

def taskgroups_progress(topic_id, student_id):
    database.submissions.sort(key=lambda x : x.time, reverse=True)
    
    for topic in database.topics:
        if topic.topic_id == topic_id:
            progress = []
            tasks_viewed = []

            for taskgroup in database.taskgroups:
                if taskgroup.taskgroup_id in topic.taskgroups:
                    taskgroup_total = 0
                    taskgroup_progress = {'unmarked': 0, 'correct': 0, 'incorrect': 0}

                    for task in database.tasks:
                        if task.taskgroup_id == taskgroup.taskgroup_id and task.answer_type != 'content':
                            for submission in database.submissions:
                                if task.task_id in submission.tasks and submission.student == student_id and task.task_id not in tasks_viewed:
                                    taskgroup_progress[submission.status] += 1
                                    tasks_viewed.append(task.task_id)
                            taskgroup_total += 1

                    if taskgroup_total > 0:
                        summary = {
                            'unmarked': 100 * taskgroup_progress['unmarked'] / taskgroup_total,
                            'correct': 100 * taskgroup_progress['correct'] / taskgroup_total,
                            'incorrect': 100 * taskgroup_progress['incorrect'] / taskgroup_total
                        }
                    else:
                        summary = {
                            'unmarked': 0,
                            'correct': 0,
                            'incorrect': 0
                        }

                    progress.append({'taskgroup':taskgroup.taskgroup_id, 'progress': summary})

            progress.sort(key=lambda tg: topic.taskgroups.index(tg['taskgroup']))
            return progress

def tasks_progress(taskgroup_id, student_id):
    tasks = []
    total = 0
    submitted = 0
    correct = 0

    database.submissions.sort(key=lambda x : x.time, reverse=True)

    for task in database.tasks:
        multiple_for_task = False
        if task.taskgroup_id == taskgroup_id and task.answer_type != 'content':
            submissions = []
            for submission in database.submissions:
                if task.task_id in submission.tasks and submission.student == student_id:
                    submissions.append(submission.json())
                    if submission.status == 'correct' and not multiple_for_task:
                        correct += 1

                    if not multiple_for_task:
                        submitted += 1
                        multiple_for_task = True

            total += 1
            tasks.append({'task':task.task_id, 'submissions':submissions})

    progress = {'tasks': tasks, 'submitted': submitted, 'correct': correct, 'total': total}

    return progress

def mark(token, submission_id, status):
    auth.authorise_user(token)

    for submission in database.submissions:
        if submission.submission_id == submission_id:
            submission.status = status

            database.update()
            return {}

def add_comment(token, submission_id, comment):
    auth.authorise_user(token)

    for submission in database.submissions:
        if submission.submission_id == submission_id:
            submission.comment = comment

            database.update()
            return {}

def recent_submissions(class_id):
    submissions = []

    for c in database.classes:
        if c.class_id == class_id:
            tasks = course_tasks(c.course)

            for submission in database.submissions:
                if submission.student in c.students and submission.tasks[0] in tasks and submission.status == 'unmarked':
                    print(tasks)
                    submission_details = submission.json()

                    for user in database.users:
                        if user.username == submission.student:
                            submission_details['student'] = {'username':user.username, 'name': user.name}
                            break

                    for task in database.tasks:
                        if task.task_id in submission.tasks:
                            submission_details['task'] = {'task_id': task.task_id, 'name': task.name}

                    submissions.append(submission_details)

    print(submissions)
    submissions.sort(key=lambda sb: sb['time'], reverse=True)
    return submissions[:20]
