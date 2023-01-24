import functools
import pyotp

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)

from werkzeug.security import check_password_hash

from Fang.Models import Author
from Fang.security import decrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')


@auth_bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        totp_code = request.form.get('totp_code')
        error = None

        user: Author = Author.query.filter_by(username=username).one_or_none()

        if not user:
            error = "Username does not match any users in the database."
        elif not check_password_hash(user.passwd_hash, password):
            flash("Failed to authenticate your password.")
            session.clear()
            abort(401)
        elif user.totp_secret and totp_code == "":
            error = "Please enter your 2FA Token."
        elif user.totp_secret and totp_code != "":
            shared_secret = decrypt(user.totp_secret, password)
            totp = pyotp.TOTP(shared_secret)
            del shared_secret
            matched: bool = totp.verify(totp_code)
            if not matched:
                error = "Failed to verify TOTP."

        if error:
            flash(error)
        else:
            return add_logged_in_user(user)

    return render_template('auth/login.html')


def add_logged_in_user(user: Author):
    session.clear()
    session['user_id'] = user.id
    return redirect(url_for('cms.index'))


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = Author.query.get(user_id)


@auth_bp.route('/logout')
def logout():
    # Clear the application session and redirect user to an unprivileged page.
    session.clear()
    flash("Successfully logged out.")
    return redirect(url_for('routes.index'))


# Function to be used as a decorator for views that need login privileges.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@auth_bp.context_processor
def auth_urls():
    return dict(is_root=True)
