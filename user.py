#user.py for user session management
from werkzeug.security import check_password_hash

#create user object
class User:
    #define constructor of user obj get username, email, and psswrd
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    #define methods of User Class

    #return true if user is authenticated
    @staticmethod
    def is_authenticated():
        return True

    #return true if user is an active user
    @staticmethod
    def is_active():
        return True

    #return true if user is anonymous
    @staticmethod
    def is_anonymous():
        return False

    #return user's unicode
    def get_id(self):
        return self.username

    #check password with password hash
    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)
