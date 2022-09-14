import os
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin


# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret' # TODO: Use this with wtforms
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {".jpg", ".png"} # Might use this at some point, probably don't want people to upload any file type
    #RECAPTCHA_PUBLIC_KEY = '6Leah_khAAAAAHx_biFobCvvrPB1ciHsBxSsr6IU'
    #RECAPTCHA_PRIVATE_KEY = '6Leah_khAAAAAIbvbtdn97A73EL6qqI5PjGTUDna'

class User(UserMixin):
    def __init__(self, id, username) -> None:
        self.id = id
        self.username = username
        self.authenticated = False

    def get_username(self):
        return self.username

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
         return False

    def is_authenticated(self):
         return self.authenticated

    def is_active(self):
         return True

    def get_id(self):
         return self.id