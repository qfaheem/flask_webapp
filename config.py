class Config:
    SECRET_KEY = 'doVHDsQHQv21ivHDnNtR7JMzBgFHhRFj366C91J6nnwqct4w'
    SQLALCHEMY_DATABASE_URI = 'postgresql://dfhuser:dfh%40U%24er90@localhost/data_filter_hub'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
