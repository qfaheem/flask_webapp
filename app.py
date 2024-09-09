# Standard Library Imports
import os
import json

# Third-Party Imports
import pandas as pd
from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_login import login_user, login_required, logout_user, current_user
from celery import Celery
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Local Imports
from src.forms import LoginForm, SignupForm, AddUserForm
from src.models.user import User
from src.models.company_data import Company
from extensions import db, migrate, login_manager

load_dotenv()
# Initialize Flask app
app = Flask(__name__, template_folder=r'src\templates', static_folder=r'src\static')

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')

# Initialize Celery
celery = Celery(
    app.name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"]
)
celery.conf.update(app.config)

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to parse request data
def get_request():
    mimetype = request.mimetype
    _request_data = {}
    if mimetype == 'application/x-www-form-urlencoded':
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

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('upload_data'))
        else:
            flash('Invalid username or password', 'danger')
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
        return render_template('uploading.html')
    return render_template('signup.html', form=form)

@celery.task
def process_file(file_path):
    with app.app_context():
        try:
            data_in_chunks = pd.read_csv(file_path, chunksize=100000)
            record = []
            for data in data_in_chunks:
                if data.columns[0] != 'sr_no':
                    data.rename(columns={data.columns[0]: 'sr_no'}, inplace=True)
                for index, row in data.iterrows():
                    new_record = Company(
                        sr_no=int(row['sr_no']),
                        name=row['name'],
                        domain=row['domain'],
                        year_founded=int(row['year founded']) if pd.notna(row['year founded']) else None,
                        industry=row['industry'],
                        size_range=row['size range'],
                        locality=row['locality'],
                        country=row['country'],
                        linkedin_url=row['linkedin url'],
                        current_employee=int(row['current employee estimate']) if pd.notna(row['current employee estimate']) else None,
                        total_employee=int(row['total employee estimate']) if pd.notna(row['total employee estimate']) else None
                    )
                    record.append(new_record)
                db.session.bulk_save_objects(record)
                db.session.commit()
                print("File processed and data added to PostgreSQL successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while processing the file: {e}")

@app.route('/upload_data', methods=['GET', 'POST'])
@login_required
def upload_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            uploads_dir = 'uploads_dir'
            os.makedirs(uploads_dir, exist_ok=True)
            filename = secure_filename(file.filename)
            file_path = os.path.join(uploads_dir, filename)
            file.save(file_path)
            process_file.delay(file_path)
    return render_template('uploading.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.clear()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@app.route('/users', methods=['GET'])
@login_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)
    return render_template('users.html', users=users)

@app.route('/query_builder', methods=['GET'])
@login_required
def query_builder():
    return render_template('query_builder.html')

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        new_user = User(username=username, email=email, password=password)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('add_user.html', form=form)


@app.route('/query_results', methods=['GET', 'POST'])
@login_required
def query_results():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    filters = {}
    for key, value in request.form.items():
        if value.strip() != "":
            if isinstance(value, str):
                value = value.lower()
            filters.update({key: value})
    filters = {key: value for key, value in filters.items() if value}
    print(filters)
    query = db.session.query(Company).filter_by(**filters)
    print(query)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items

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

# Run the app
if __name__ == "__main__":
    app.run(debug=os.getenv('DEBUG') or False, port=os.getenv('PORT') or 5000)
