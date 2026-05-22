import os
import warnings
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask import Flask
from app.models import User, db
from flask_login import LoginManager, login_manager
from app.routes.web_routes import web
from app.routes.api_routes import api
from app.routes.admin_routes import admin
warnings.filterwarnings("ignore", category=UserWarning)

db = SQLAlchemy()
manage_login = LoginManager()

load_dotenv()
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kunci_rahasia_cadangan_lokal')
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = None
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/db_puskesmas')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from app.models import db, User
    db.init_app(app)
    
    app.register_blueprint(web)
    app.register_blueprint(api)
    app.register_blueprint(admin)
    
    
    
    manage_login.init_app(app)
    manage_login.login_view = 'web.login'
    
    @manage_login.user_loader
    def load_user(uid): 
     return User.query.get(int(uid))
    
    
    return app