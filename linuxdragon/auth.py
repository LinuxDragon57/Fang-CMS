import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)
from werkzeug.security import check_password_hash

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


@login_required
def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = session.get('user_id')
        admin_status: bool = all(db.session.execute(db.select(Author.admin).where(Author.id == user_id)).first())
        if admin_status:
            return abort(401)
        return view(**kwargs)

    return wrapped_view
