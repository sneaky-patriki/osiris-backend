import os
from time import time
from flask import send_from_directory
from data_store import database, Attachment
from error import InputError, AccessError

def add(token, task_id, cover_name, attachment):
    auth.authorise_user(token)

    for task in database.tasks:
        if task.task_id == task_id:
            attachment_id = database.generate_id('attachment')
            task.attachments.append(attachment_id)

            filename = attachment.filename
            new_attachment = Attachment(attachment_id, task_id, cover_name, filename)
            database.attachments.append(new_attachment)

            attachment.save(os.path.join('Attachments', filename))
            task.modified = time()

            break

    database.update()
    return {'attachment': {'attachment_id':attachment_id, 'name': cover_name}}

def delete(token, attachment_id):
    auth.authorise_user(token)

    for attachment in database.attachments:
        if attachment.attachment_id == attachment_id:
            database.attachments.remove(attachment)

            for task in database.tasks:
                if task.task_id == attachment.task_id:
                    task.attachments.remove(attachment_id)
                    break

            break

    database.update()

def listall(token, task_id):
    auth.authorise_user(token)

    attachments = []
    for attachment in database.attachments:
        if attachment.task_id == task_id:
            details = {'attachment_id': attachment.attachment_id,
                       'cover_name': attachment.cover_name,
                       'url':f'http://127.0.0.1:8080/tasks/attachments/retrieve?attachment_id={attachment.attachment_id}'
                       }
            attachments.append(details)

    return {'attachments': attachments }

def retrieve(attachment_id):
    for attachment in database.attachments:
        if attachment.attachment_id == attachment_id:
            return send_from_directory('Attachments/', attachment.storage_name)
