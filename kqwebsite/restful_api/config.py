DB_USER = 'root'
DB_PASSWORD = 'admin'
DB_HOST = '47.103.40.112'
DB_DB = 'admin'

DEBUG = True
PORT = 5000
HOST = "0.0.0.0"

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + '/' + DB_DB