import pandas as pd
from .models.company_data import Company  # Import your User model
from .models import db  # Import your database instance
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery

# app = Flask(__name__)
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # Change as per your Redis configuration
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# celery = make_celery(app)

# @celery.task
def process_file(file_path):
    try:
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)

        # Iterate over the rows of the DataFrame and save to PostgreSQL
        for index, row in df.iterrows():
            new_record = Company(
                sr_no=row['sr_no'],
                name=row['name'],
                domain=row['domain'],
                year_founded=row['year founded'],
                industry=row['industry'],
                size_range=row['size range'],
                locality=row['locality'],
                country=row['country'],
                linkedin_url=row['linkedin url'],
                current_employee=row['current employee'],
                total_employee=row['total employee']
            )
            db.session.add(new_record)

        db.session.commit()  # Commit the transaction
        print("File processed and data added to PostgreSQL successfully.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"An error occurred while processing the file: {e}")
