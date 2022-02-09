from flask import Flask
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)

    # TODO: add stuff related to config and database
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # TODO: use the user_id to get correct user from database
        return User()

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app