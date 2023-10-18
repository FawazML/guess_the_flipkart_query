from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
#csrf = CSRFProtect()
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=7)
app.secret_key = '461a641ce68ef984303c432450737368'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbmodel.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Upload folder
# UPLOAD_FOLDER = r"static\files"

db = SQLAlchemy(app)
#csrf.init_app(app)