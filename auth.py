import hashlib
from uuid import uuid4

from data_store import database
from error import AccessError, InputError

def generate_token(username):
    token = str(uuid4())
    database.active_tokens[token] = username
    database.update()
    return token

def login(username, password):

    encoder = hashlib.sha224()
    encoder.update(password.encode('utf-8'))
    hashed_password = encoder.hexdigest()

    authenticated = database.authenticate_user(username, hashed_password)

    if not authenticated:
        raise AccessError('Invalid username or password')

    return { 'username':username, 'token': generate_token(username),
              'user_type': authenticated}

def logout(token):

    try:
        del database.active_tokens[token]
    except:
        pass

    database.update()

    return {}
