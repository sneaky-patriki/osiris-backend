import hashlib
from uuid import uuid4

from models import ActiveToken, User
from error import AccessError, InputError

def generate_token(user_id):
    token = str(uuid4())
    ActiveToken.create(user=user_id, token=token)
    return token

def authorise_user(token):
    activetoken = ActiveToken.select().where(ActiveToken.token == token)
    try:
        activetoken = activetoken.get()
    except:
        raise AccessError('Unauthorised User')

    return activetoken.user_id

def login(username, password):

    encoder = hashlib.sha224()
    encoder.update(password.encode('utf-8'))
    hashed_password = encoder.hexdigest()
    print(hashed_password)
    # authenticated = database.authenticate_user(username, hashed_password)
    user = User.select().where((User.username == username) & (User.password == hashed_password))
    print(user)
    if not user:
        raise AccessError('Invalid username or password')

    user = user.get()

    return { 'username':username, 'token': generate_token(user.id),
              'user_type': user.user_type}

def logout(token):

    try:
        del database.active_tokens[token]
    except:
        pass

    database.update()

    return {}
