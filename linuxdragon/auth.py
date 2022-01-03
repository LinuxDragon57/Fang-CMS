import functools
from secrets import compare_digest

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, abort)
from werkzeug.security import generate_password_hash, check_password_hash

from linuxdragon.Models import db, Author

auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')


@auth_bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        error = None

        user = Author.query.filter_by(username=username).one_or_none()

        if not user:
            error = "Username does not match any users in the database."
        elif not check_password_hash(user.passwd_hash, password):
            error = "Incorrect Password."

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('cms.index'))

        flash(error)

    return render_template('auth/login.html')


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = Author.query.get(user_id)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Successfully logged out.")
    return redirect(url_for('routes.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@auth_bp.route('/account_settings', methods=("GET", "POST"))
@login_required
def account_settings():
    if request.method == "POST":
        if request.form.get('cancel') == 'Cancel':
            return redirect(url_for('cms.index'))
        elif request.form.get('update') == 'Update':
            current_user = Author.query.get(session.get('user_id'))
            username = request.form.get('username')
            new_password = request.form.get('newPassword')
            repeat_password = request.form.get('repeatPassword')
            password = request.form.get('password')
            error = None

            if not check_password_hash(current_user.passwd_hash, password):
                error = "Incorrect Password."

            if not compare_digest(new_password, repeat_password):
                error = "New passwords do not match."

            if error is None:
                if len(username) > 1:
                    current_user.username = username
                if len(new_password) > 1 and len(repeat_password) > 1:
                    current_user.passwd_hash = generate_password_hash(new_password)
                db.session.commit()
                flash(f"Successfully updated your user settings, {current_user.username}")

            flash(error)

    return render_template('auth/user_settings.html')