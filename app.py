from flask import Flask, render_template, redirect, url_for, flash, request
from app.forms import LoginForm, SignupForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
# from app.models import User
from flask_migrate import Migrate
# from config import Config
# from extensions import db
from app.models.user import User

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SECRET_KEY'] = 'doVHDsQHQv21ivHDnNtR7JMzBgFHhRFj366C91J6nnwqct4w'
# Configure your PostgreSQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dfhuser:dfh@U$er90@localhost/data_filter_hub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# users = {}
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# def create_app():
#     app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
#     app.config.from_object(Config)

#     register_extension(app)

#     return app

# def register_extension(app):
#     db.init_app(app)
#     migrate = Migrate(app, db)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(request)
    if form.validate_on_submit():
        flash('Login Requested for user {}'
              .format(form.username))
        return redirect(url_for('landing'))
    return render_template('login.html', form=form)  # Pass the form to the template



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    print(form)
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        print("email: ",email)
        print("pass: ", password)
        # Store user details in the in-memory dictionary
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()  # Save changes to the database
        # users[username] = {'email': email, 'password': password}
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('landing'))
    
    return render_template('signup.html', form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)



# # run.py

# from app import create_app

# app = create_app()

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', debug=True)
