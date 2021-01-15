from models import User, ActiveToken

def authenticate_user(username, hashed_password):
    user = User.select().where(User.username == username & user.password == hashed_password)
    if user:
        return user.get().user_type
    return False

def authorise_user(token):
    found = ActiveToken.select().where(ActiveToken.token == token)
    if not found:
        raise AccessError('Unauthorised User')

def get_user(username):
    user = User.select().where(User.username == username)
    if not user:
        raise ValueError('Username given was invalid')

def generate_id(self, object_type):
    result = 1

    if object_type in self.next_id:
        result = self.next_id[object_type]
        self.next_id[object_type] += 1
    else:
        self.next_id[object_type] = 2

    return result
