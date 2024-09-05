# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from celery import Celery, Task


# db = SQLAlchemy()
# migrate = Migrate()
# # celery = Celery(__name__)
# # celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
# # celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# # def make_celery(app):
# #     celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
# #     # celery.conf.update(app.config)
# #     # return celery
# #     celery.conf.update(
# #         broker=app.config['CELERY_BROKER_URL'],
# #         backend=app.config['CELERY_RESULT_BACKEND']
# #     )
# #     return celery

# # def celery_init_app(app: Flask):
# #     class FlaskTask(Task):
# #         def __call__(self, *args, **kwargs):
# #             with app.app_context():
# #                 return self.run(*args, **kwargs)
# #     celery_app = Celery(app.name, task_cls=FlaskTask)
# #     celery_app.config_from_object(app.config["CELERY"])
# #     celery_app.set_default()
# #     app.extensions["celery"] = celery_app
# #     return celery_app


# def create_app():
#     app = Flask(__name__, template_folder='templates', static_folder='static')
#     print("\t\t ============== before config \n", app.config)
#     app.config['SECRET_KEY'] = 'doVHDsQHQv21ivHDnNtR7JMzBgFHhRFj366C91J6nnwqct4w'
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dfhuser:dfh%40U%24er90@localhost/data_filter_hub'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     # app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'  # Change as per your Redis configuration
#     # app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'
#     print("\t\t ============== after config \n",app.config)
#     # celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
#     # celery.conf.update(app.config)
#     # app.config.from_mapping(
#     #     CELERY=dict(
#     #         broker_url="redis://localhost",
#     #             result_backend="redis://localhost",
#     #             task_ignore_result=True,
#     #         ),
#     #     )
#     # celery_app = celery_init_app(app)
#     db.init_app(app)
#     migrate.init_app(app, db)
#     # Import and initialize routes
#     from .routes import init_routes
#     init_routes(app)
#     # celery = make_celery(app)
#     # celery.conf.update(app.config)
#     # celery_app = celery_init_app(app)
 
#     return app