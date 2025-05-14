from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os
from flask import redirect, url_for
from flask_login import current_user



# init extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)


    # register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    from app.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # home route
    @app.route('/')
    def index():
        from app.auth import bp as auth_bp
        from app.tasks import bp as tasks_bp
        if current_user.is_authenticated:
            return redirect(url_for('tasks.dashboard'))
        return redirect(url_for('auth.login'))

    return app