import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'doVHDsQHQv21ivHDnNtR7JMzBgFHhRFj366C91J6nnwqct4w'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://dfhuser:dfh@U$er90@localhost/data_filter_hub'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = 'redis://localhost:6380/0'  # Change as per your Redis configuration
    CELERY_RESULT_BACKEND = 'redis://localhost:6380/0'
    