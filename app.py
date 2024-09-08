from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify, current_app
from celery import Celery
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from src.forms import LoginForm, SignupForm
from src.models.user import User
from src.models.company_data import Company
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import time
import os
import json
from extensions import db, migrate, login_manager
import pandas as pd

app = Flask(__name__, template_folder=r'src\templates',
            static_folder=r'src\static')

app.config["SECRET_KEY"] = "doVHDsQHQv21ivHDnNtR7JMzBgFHhRFj366C91J6nnwqct4w"
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://dfhuser:dfh%40U%24er90@localhost/data_filter_hub'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Change as per your Redis configuration
app.config["CELERY_BROKER_URL"] = 'redis://127.0.0.1:6379/0'
app.config["CELERY_RESULT_BACKEND"] = 'redis://127.0.0.1:6379/0'

# db = SQLAlchemy()
# migrate = Migrate()
celery = Celery(
    app.name, broker=app.config["CELERY_BROKER_URL"], backend=app.config["CELERY_RESULT_BACKEND"])
celery.conf.update(app.config)
# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6380/0")
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://17.0.0.1:6380/0")
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'


# Define the user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_request():
    mimetype = request.mimetype
    _request_data = {}
    if mimetype == 'application/x-www-form-urlencoded':
        print(request.form)
        _request_data = json.loads(next(iter(request.form.keys())))
    elif mimetype == 'multipart/form-data':
        _request_data = dict(request.form)
    elif mimetype == 'application/json':
        _request_data = request.json
    else:
        _request_data = request.data.decode()
    if _request_data == "":
        _request_data = {}
    return _request_data


@celery.task
def delay_func():
    print("delayed task !!!")
    time.sleep(5)


@app.route("/testing")
def test():
    delay_func.delay()
    return "Hello Testing !!!"


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = LoginForm()
    print("=====", form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # user = User.get_by_email(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            # # return redirect(url_for('upload_data'))
            next_page = request.args.get('next')  # Get the 'next' parameter
            return redirect(next_page or url_for('upload_data'))
            # return render_template('uploading.html')
        else:
            flash('Invalid username or password', 'danger')
    # flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        new_user = User(username=username, email=email, password=password)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Account created successfully! Please log in.', 'success')
        # return redirect(url_for('upload_data'))
        return render_template('uploading.html')
    return render_template('signup.html', form=form)


@celery.task
def process_file(file_path):
    with app.app_context():
        try:
            # Load the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)
            print("inside indezx")

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


@app.route('/upload_data', methods=['GET', 'POST'])
@login_required
def upload_data():
    print("request in upload data ")
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            # Ensure the 'uploads' directory exists
            uploads_dir = 'uploads_dir'
            os.makedirs(uploads_dir, exist_ok=True)
            filename = secure_filename(file.filename)
            # Ensure 'uploads' folder exists
            file_path = os.path.join('uploads_dir', filename)
            print(file_path)
            file.save(file_path)
            task = process_file.delay(file_path)  # Trigger the Celery task
            # flash('File uploaded and processing started!', 'success')
            # return jsonify({"task_id": task.id, "status": "File processing started!"})
            # return redirect(url_for('upload_data'))
    # return {"message":"uploaded"}
    return render_template('uploading.html')  # Ensure this template exists


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.clear()  # Clear the session data
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))


@app.route('/users', methods=['GET'])
@login_required
def manage_users():
    print("current : ", current_user)
    page = request.args.get('page', 1, type=int)
    # Adjust per_page as needed
    users = User.query.paginate(page=page, per_page=10)
    return render_template('users.html', users=users)


@app.route('/query_builder', methods=['GET'])
@login_required
def query_builder():
    # Render the form
    return render_template('query_builder.html')


@app.route('/query_results', methods=['GET', 'POST'])
@login_required
def query_results():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Collect filters from the form
    filters = {}
    for key, value in request.form.items():
        if value.strip() != "":
            filters.update({key: value})
    filters = {key: value for key, value in filters.items() if value}

    # Build the query
    query = db.session.query(Company).filter_by(**filters)

    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items

    # Convert results to a list of dictionaries
    final_response = []
    for row in results:
        data = {
            "name": row.name or None,
            "domain": row.domain or None,
            "year_founded": row.year_founded or None,
            "industry": row.industry or None,
            "size_range": row.size_range or None,
            "locality": row.locality or None,
            "country": row.country or None,
            "linkedin_url": row.linkedin_url or None,
            "current_employee": row.current_employee or None,
            "total_employee": row.total_employee or None,
        }
        final_response.append(data)

    if not final_response:
        return render_template('query_builder.html', message='No data found', filters=filters)

    return render_template('query_result.html', data=final_response, filters=filters, pagination=pagination)


if __name__ == "__main__":
    app.run(debug=True)
