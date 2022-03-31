from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
from flask_mail import Mail

# Database created
db = SQLAlchemy()
def create_app():
    global app 
    global mail
    app = Flask(__name__)
    # mail.init_app(app)
    @app.before_first_request
    def create_tables():
        db.create_all()
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # TODO: add stuff related to config and database
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    app.config['SECRET_KEY'] = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

        # main config
    app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'

    # mail settings
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    # gmail authentication
    app.config['MAIL_USERNAME'] = os.environ['APP_MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['APP_MAIL_PASSWORD']

    # mail accounts
    app.config['MAIL_DEFAULT_SENDER'] = 'purduecircle265@gmail.com'

    mail = Mail(app)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # TODO: use the user_id to get correct user from database
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for main runner of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for profile related features
    from .profile import prof as prof_blueprint
    app.register_blueprint(prof_blueprint)

    # blueprint for post related functions
    from .posts import posts as posts_blueprint
    app.register_blueprint(posts_blueprint)

    return app