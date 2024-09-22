import os

class Config:
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'cubom882001@gmail.com'
    MAIL_PASSWORD = 'rzac qtqo xpkr uuzc'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SECRET_KEY = 'rzac qtqo xpkr uuzc'
    DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
