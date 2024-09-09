from flask import Flask
from .extensions import db, migrate, login_manager
from .celery_config import make_celery

def create_app():
    app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
    
    # Load configuration
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    celery = make_celery(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.file import file_bp
    from .routes.query import query_bp
    from .routes.user_management import user_management_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(user_management_bp)
    
    return app
