from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from src.forms import LoginForm, SignupForm
from src.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import time, os

app = Flask(__name__,template_folder=r'src\templates', static_folder=r'src\static')

app.config["SECRET_KEY"] = "doVHDsQHQv21ivHDnNtR7JMzBgFHhRFj366C91J6nnwqct4w"
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://dfhuser:dfh@U$er90@localhost/data_filter_hub'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["CELERY_BROKER_URL"] = 'redis://localhost:6379/0'  # Change as per your Redis configuration
app.config["CELERY_RESULT_BACKEND"] = 'redis://localhost:6379/0'

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
db.init_app(app)
migrate.init_app(app, db)

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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['logged_in'] = True 
            print("working",user.password)
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
            file_path = os.path.join('uploads_dir', filename)  # Ensure 'uploads' folder exists
            print(file_path)
            file.save(file_path)
            # task = process_file(file_path)  # Trigger the Celery task
            # flash('File uploaded and processing started!', 'success')
            # return jsonify({"task_id": task.id, "status": "File processing started!"})
            # return redirect(url_for('upload_data'))
    return {"message":"uploaded"}
    # return render_template('upload_data.html')  # Ensure this template exists

@app.route('/logout')
def logout():
    session.pop('logged_in', None) 
    session.clear()  # Clear the session data
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))


@app.route('/users', methods=['GET', 'POST'])
def manage_users():
    users = User.query.all()  # Fetch all users
    return render_template('users.html', users=users)

@app.route('/query_builder')
def query_builder():
    return render_template('query_builder.html')

if __name__ == "__main__":
    app.run(debug=True)