#import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from blogDragon.Models import db, Author


auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')


@auth_bp.route('setup', methods=('GET', 'POST'))
def access_control_manager():
    from blogDragon.access import first_time
    access_control_variable: bool = first_time
    py_file = open('access.py', 'w')
    py_file.truncate()
    py_file.write("first_time: bool = False\n")
    py_file.close()
    return setup(access_control_variable)


def setup(first_time=False):
    if request.method == "POST" and first_time is True:
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif not name:
            error = "Name is required."

        if error is None:
            Author.create(usrname={username}, name={name},
                          passwd_hash=generate_password_hash(password), admin=True)
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    elif not first_time:
        page_error = "You are not permitted to access this resource at this time."
        flash(page_error)

    return render_template('auth/setup.html')


@auth_bp.route('login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = Author.get(Author.usrname == username)

        if user is None:
            error = 'Please enter your username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect Password.'

        if error is None:
            session.clear()
            session['user_id'] = Author.get_by_id(user)
            return redirect(url_for('console'))

        flash(error)

    return render_template('auth/login.html')


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = Author.get_by_id('user_id')


@auth_bp.route('logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
