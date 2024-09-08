from flask import render_template, flash, redirect, url_for, request, session, jsonify
from .forms import LoginForm, SignupForm
import pandas as pd
import os
from werkzeug.utils import secure_filename
from .models.user import User  # Import models here to avoid circular imports
from .models.company_data import Company
from celery import shared_task
from . import db
from celery import Celery, Task


def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def init_routes(app):

    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    celery_app = celery_init_app(app)

    @app.route('/')
    def landing():
        return render_template('landing.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                session['logged_in'] = True
                print("working", user.password)
                flash('Login successful!', 'success')
                return redirect(url_for('upload'))
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
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('upload'))
        return render_template('signup.html', form=form)

    @app.route('/uploading', methods=['GET', 'POST'])
    def upload():
        return render_template('uploading.html')

    @celery_app.task(name="app.test_task")
    # @shared_task(ignore_result=False)
    def test_task():
        print("Test task executed!")
        return "Task completed!"

    @app.route('/test_task')
    def run_test_task():
        test_task.delay()
        return "Test task triggered!"

    # @app.route('/users', methods=['GET', 'POST'])
    # def users():
    #     user_list = User.query.all()  # Retrieve all users from the database
    #     form = AddUserForm()

    #     if form.validate_on_submit():
    #         username = form.username.data
    #         email = form.email.data
    #         password = generate_password_hash(form.password.data)  # Ensure to hash the password
    #         new_user = User(username=username, email=email, password=password, is_active=True)  # Default to active
    #         db.session.add(new_user)
    #         db.session.commit()
    #         flash('User added successfully!', 'success')
    #         return redirect(url_for('users'))

    #     return render_template('users.html', users=user_list, form=form)

    @app.route('/users', methods=['GET', 'POST'])
    def manage_users():
        users = User.query.all()  # Fetch all users
        return render_template('users.html', users=users)

    @app.route('/add_user', methods=['GET', 'POST'])
    def add_user():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash('User added successfully!', 'success')
            return redirect(url_for('manage_users'))

        return render_template('add_user.html')

    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        session.clear()  # Clear the session data
        flash('You have been logged out.', 'info')
        return redirect(url_for('landing'))

    # @celery_app.task(bind= True)
    # @shared_task(ignore_result=False)/
    def process_file(file_path):
        chunk_size = 100
        # Your logic to process the uploaded file and store the data in PostgreSQL
        # try:
        print("file_path", file_path)
        print("IN A TRY BLOCK")
        # # Load the CSV file into a pandas DataFrame
        # df = pd.read_csv(file_path)
        # df.columns = df.columns.str.strip()  # Clean up column names

        # # Ensure 'year_founded' is numeric
        # df['year founded'] = pd.to_numeric(df['year founded'], errors='coerce')

        # # Optionally, drop rows where 'year founded' couldn't be converted
        # df.dropna(subset=['year founded'], inplace=True)

        # # Convert 'year founded' to an integer (if applicable)
        # df['year founded'] = df['year founded'].astype(int)

        # new changes =v0.2
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            print("CHUNK SIZE INSIDE")
            records = []
            # Clean and preprocess the data
            chunk.columns = chunk.columns.str.strip()  # Clean up column names

            # Ensure 'year founded' is numeric and clean the data
            chunk['year founded'] = pd.to_numeric(
                chunk['year founded'], errors='coerce')
            # Drop rows with NaN 'year founded'
            chunk.dropna(subset=['year founded'], inplace=True)
            chunk['year founded'] = chunk['year founded'].astype(
                int)  # Convert to integer
            if chunk.columns[0] != 'sr_no':
                chunk.rename(columns={chunk.columns[0]: 'sr_no'}, inplace=True)
            # Iterate over the rows of the DataFrame and save to PostgreSQL
            for index, row in chunk.iterrows():
                print("Current Index: ", index)
                new_record = Company(
                    sr_no=int(row['sr_no']),
                    name=str(row['name']),
                    domain=str(row['domain']),
                    year_founded=int(row['year founded']),
                    industry=str(row['industry']),
                    size_range=str(row['size range']),
                    locality=str(row['locality']),
                    country=str(row['country']),
                    linkedin_url=str(row['linkedin url']),
                    current_employee=int(row['current employee estimate']),
                    total_employee=int(row['total employee estimate'])
                )
                records.append(new_record)
                # db.session.add(new_record)

        # db.session.commit()  # Commit the transaction

        # new change _v0.2
        db.session.bulk_save_objects(records)
        db.session.commit()
        # Update the task state with progress
        # self.update_state(state='PROGRESS', meta={'current': chunk.index[-1], 'total': len(chunk)})
        print("File processed and data added to PostgreSQL successfully.")
        return {'status': 'Completed'}
        # except Exception as e:
        #     db.session.rollback()  # Rollback in case of error
        #     print(f"An error occurred while processing the file: {e}")

    @app.route('/task_status/<task_id>')
    def task_status(task_id):
        task = process_file.AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'progress': 0,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'progress': task.info.get('current', 0),
                'total': task.info.get('total', 0),
                'status': 'Processing...' if task.state == 'PROGRESS' else 'Completed'
            }
        else:
            response = {
                'state': task.state,
                'progress': 0,
                'status': str(task.info)  # Error message
            }
        return jsonify(response)

    @app.route('/upload_data', methods=['GET', 'POST'])
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
                task = process_file(file_path)  # Trigger the Celery task
                # flash('File uploaded and processing started!', 'success')
                return jsonify({"task_id": task.id, "status": "File processing started!"})
                # return redirect(url_for('upload_data'))
        return {"message": "uploaded"}
        # return render_template('upload_data.html')  # Ensure this template exists

    @app.route('/query_builder')
    def query_builder():
        return render_template('query_builder.html')

    # @app.route('/manage_users')
    # def manage_users():
    #     users = User.query.all()  # Get all users from the database
    #     return render_template('manage_users.html', users=users)

    # @app.route('/add_user', methods=['GET', 'POST'])
    # def add_user():
    #     # Logic for adding a user
    #     return render_template('add_user.html')
