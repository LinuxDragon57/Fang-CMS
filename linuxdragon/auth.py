import functools
import pyotp

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response, abort, current_app
)

from werkzeug.security import check_password_hash
from itsdangerous import Signer

from linuxdragon.Models import Author
from linuxdragon.security import decrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')


def get_app_signature():
    return Signer(current_app.config['SECRET_KEY'])


@auth_bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        error = None

        user: Author = Author.query.filter_by(username=username).one_or_none()

        if not user:
            error = "Username does not match any users in the database."
        elif not check_password_hash(user.passwd_hash, password):
            flash("Failed to authenticate your password.")
            session.clear()
            abort(401)

        if not error:
            session.clear()
            signature = get_app_signature()
            response = make_response(redirect(url_for('auth.verify_auth')))
            response.set_cookie(
                key='pre-auth',  # Use itsdangerous.Signer to create a tamper-resistant cookie
                value=signature.sign(str(user.id)).decode(),
                path=url_for('auth.verify_auth'),
                max_age=90,
                secure=True,
                httponly=True
            )
            return response

        flash(error)

    return render_template('auth/login.html')


@auth_bp.route('/verify-auth', methods=("GET", "POST"))
def verify_auth():
    user_id = None
    signature = get_app_signature()
    pre_auth_cookie = request.cookies.get("pre-auth")
    if pre_auth_cookie:
        user_id = int(signature.unsign(pre_auth_cookie.encode()))
    else:
        abort(401)
    if user_id:  # Ensure the user_id has a non-null value.
        user = Author.query.get(user_id)  # Access an instance of the Author class by its id.
        if user.totp_secret is None:  # If the user doesn't have an MFA method set up.
            return add_logged_in_user(user)
        elif user.totp_secret:  # If the user has TOTP set up.
            if request.method == "POST":
                password = request.form.get('password')
                totp_code = request.form.get('totp_code')
                shared_secret = str(decrypt(user.totp_secret, password))
                totp = pyotp.TOTP(shared_secret)
                del shared_secret  # Remove the shared_secret from memory as soon as we are done with it.
                if totp.verify(totp_code):
                    return add_logged_in_user(user)
                else:
                    flash("Failed to verify TOTP Method.")
                    # Replace the former 'pre-auth' cookie with an expired cookie that has a NULL value,
                    # and return a 401 HTTP Status Code.
                    response = make_response(abort(401))
                    response.delete_cookie('pre-auth')
                    return response
            else:
                return render_template('auth/totp.html')
    else:
        flash("The time limit to enter TOTP code was exceeded.")
        abort(408)


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
