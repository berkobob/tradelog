from os import environ, urandom
from flask import Flask
from src.view.web import web
from src.common.database import DB

app = Flask(__name__)
app.register_blueprint(web)

try:
    app.config.from_object('config.'+app.config['ENV'])
except:
    pass

if 'DB_URL' not in app.config.keys():
    app.config['DB_URL'] = environ.get('DB_URL')

if app.config['SECRET_KEY'] is None:
    app.config['SECRET_KEY'] = urandom(24)

result = DB.connect(app.config['DB_URL'], app.config['ENV'])

if not result.success:
    print ("*** FATAL ERROR. Cannot connect to database ***")
    print(result.message)
    exit()
else: print(" * Succesfully connected to the database *")