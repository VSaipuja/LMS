from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pathlib import Path

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'lms-dev-secret-key-change-in-production'
    basedir = Path(__file__).resolve().parent.parent
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{basedir / "instance" / "lms.db"}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.courses import courses_bp
    from app.routes.quizzes import quizzes_bp
    from app.routes.admin import admin_bp
    from app.routes.learning import learning_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(learning_bp)

    return app
