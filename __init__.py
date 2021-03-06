from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from models import *
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'osmefanfogoafoasq'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///system.db" 
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)    


    return app

if __name__ == "__main__":
    create_app().run()