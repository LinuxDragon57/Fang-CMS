import os
import sys
import click
import pyotp

from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from segno import make as create_qrcode
from sqlalchemy.exc import ProgrammingError

from Fang.Models import db, Author, TOTPSecret
from Fang.security import decrypt, encrypt, change_password, scrub_input_data


# Function allows the user to initialize the database with a simple Flask command.
# It merely makes a call to the db object in the application's SQLAlchemy Models.
@click.command('init-db')
@with_appcontext
def initialize_database():
    db.create_all()
    click.echo("Database Initialized!")

    return 0


# Function allows the user to expunge the database with a single Flask command.
@click.command('expunge-db')
@with_appcontext
def expunge_database():
    if click.confirm("Are you sure you want to clear the database of all tables?"):
        db.drop_all()
        click.echo("Database Expunged.")
    else:
        click.echo("Aborted")

    return 0


def cli_login(iteration: int = 1):
    error: bool = False
    username = click.prompt('Username')
    password = click.prompt('Password', hide_input=True)
    cli_user: Author = Author.query.filter_by(username=username).one_or_none()

    if not cli_user:
        click.echo("Username does not match any users in the database.", file=sys.stderr)
        error = True
    elif not check_password_hash(cli_user.passwd_hash, password):
        click.echo("Failed to authenticate your password.", file=sys.stderr)
        error = True

    if error and iteration <= 3:
        return cli_login(iteration=iteration+1)
    elif not error:
        return cli_user, password
    else:
        click.echo("Maximum number of tries exceeded. Exiting now...", file=sys.stderr)
        sys.exit(1)


@click.command('create-author')
@click.option('--username', prompt=True)
@click.password_option()
@click.option('--admin', is_flag=True)
@with_appcontext
def create_author(username: str, password: str, admin: bool):
    # Prompt for the new user's username, password, and full name.
    first_name = click.prompt("Enter author's first name", type=str)
    last_name = click.prompt("Enter author's last name", type=str)
    error = None

    if not scrub_input_data(username, password, first_name, last_name):
        error = \
            """
                Invalid arguments or missing requirements:
                    ~ Whitespace isn't allowed in password and username fields.
                    ~ The username must be at least 8 characters long.
                    ~ The password field must be at least 32 characters long.
                    ~ Name fields can only contain letters.
                    ~ Empty strings aren't allowed.
                """

    # If there is no error, continue with the program
    if error is None:
        # Look in the database for rows with a username matching the supplied username.
        try:
            if Author.query.filter_by(username=username).first() is None:
                user = Author(
                    username=username,
                    passwd_hash=generate_password_hash(password),
                    first_name=first_name,
                    last_name=last_name,
                    admin=admin
                )
                db.session.add(user)
                db.session.commit()
                if admin:
                    click.echo(f"Successfully added {username} as an Admin.")
                elif not admin:
                    click.echo(f"Successfully added {username}.")

                if click.confirm("Would you like to set up TOTP?"):
                    configure_totp(user, password)
        except ValueError as err:
            error = f"{err} {username} is already registered."

    if error:
        click.echo(error, file=sys.stderr)

    return 0


@click.command('delete-author')
@with_appcontext
def delete_author():
    current_user, password = cli_login()
    if click.confirm(f"Are you sure you want to delete the author: {current_user.full_name}? "):
        if current_user.totp_secret:
            os.remove(f"{current_app.config['DATA_DIRECTORY']}/authors/{current_user.username}.totp_qrcode.svg")
            db.session.delete(current_user.totp_secret)
        db.session.delete(current_user)
        db.session.commit()
        click.echo(f"Successfully deleted Author {current_user.full_name}.")

        return 0


@click.command('modify-author')
@click.option('--modification-choice', type=click.Choice(['username', 'password'], case_sensitive=False))
@with_appcontext
def modify_author(modification_choice):
    current_user, password = cli_login()
    if modification_choice == 'username':
        current_user.username = click.prompt("Enter new username: ")
    elif modification_choice == 'password':
        change_password(password, password, current_user)

    db.session.commit()
    click.echo(f"Successfully updated {current_user.full_name}'s settings.")

    return 0


# A function that allows the user to set up TOTP directly with a Flask command.
@click.command('reset-totp')
@with_appcontext
def reset_totp():
    # There is a known bug wherein this function causes click to throw an error...
    # Error: Got unexpected extra argument (reset-totp)
    # I can't find the bug so that I can remove it.
    current_user, password = cli_login()
    if current_user.totp_secret is not None:
        click.echo("You are about to erase your current TOTP Secret.")
        click.echo("Any previously configured TOTP credentials will no longer be able to be used for authentication.")
        if click.confirm("Are you sure you want to proceed? This action cannot be undone."):
            svg_path = f"{current_app.config['DATA_DIRECTORY']}/authors/{current_user.username}.totp_qrcode.svg"
            os.remove(svg_path)
            db.session.delete(current_user.totp_secret)
            db.session.commit()
        else:
            click.echo("Aborted")
            sys.exit(0)
    configure_totp(current_user, password)

    return 0


@click.command('test-totp')
@with_appcontext
def test_totp():
    current_user, password = cli_login()
    totp_code = click.prompt("Enter 6-digit authentication code", type=str)
    shared_secret = decrypt(current_user.totp_secret, password)
    totp = pyotp.TOTP(shared_secret)
    del shared_secret
    click.echo('\n' + ('-'*15))
    if totp.verify(totp_code):
        click.echo("VERIFIED")
    else:
        click.echo("DENIED")
    click.echo(('-'*15) + '\n')


@click.command('mkdatadirs')
@with_appcontext
def initialize_data_directories():
    # If the "DATA_DIRECTORY" specified in the TOML file doesn't exist, create it.
    try:
        if not os.path.isdir(current_app.config['DATA_DIRECTORY']):
            os.mkdir(current_app.config['DATA_DIRECTORY'])
    except FileNotFoundError:
        click.echo(f"{current_app.config['DATA_DIRECTORY']}: No such file or directory", file=sys.stderr)
        sys.exit(1)
    # If the "entries" directory doesn't exist, create it.
    if not os.path.isdir(f"{current_app.config['DATA_DIRECTORY']}/entries"):
        os.mkdir(f"{current_app.config['DATA_DIRECTORY']}/entries")

    # Same thing for the "authors" directories.
    if not os.path.isdir(f"{current_app.config['DATA_DIRECTORY']}/authors"):
        os.mkdir(f"{current_app.config['DATA_DIRECTORY']}/authors")

    # Create a directory to store application logs - Errors in particular
    if not os.path.isdir(f"{current_app.config['DATA_DIRECTORY']}/logs"):
        os.mkdir(f"{current_app.config['DATA_DIRECTORY']}/logs")

    # Iterate through the available "GENRES" defined in the TOML file
    # and create directories for them if they do not exist
    for genre in current_app.config['GENRES']:
        genre_path = f"{current_app.config['DATA_DIRECTORY']}/entries/{make_path(genre)}"
        if not os.path.isdir(genre_path):
            os.mkdir(genre_path)

    # If the database wasn't initialized beforehand, initialize the database and then try again.
    for iteration in range(0, 1):
        try:
            for author in Author.query.all():
                if not os.path.isdir(f"{current_app.config['DATA_DIRECTORY']}/authors/{author.username}"):
                    os.mkdir(f"{current_app.config['DATA_DIRECTORY']}/authors/{author.username}")
                else:
                    click.echo(f"Directory for user, {author}, has already been created.")
            break
        except ProgrammingError:
            click.echo("Unable to access the Author table. Did you initialize the database first?", file=sys.stderr)
            click.echo("Attempting to initialize database...")
            db.create_all()
            click.echo("Database Initialized!")

    # Notify the user of success at completion of the function.
    print(f"\nSuccessfully created the paths at {current_app.config['DATA_DIRECTORY']}/entries:")
    print(*os.listdir(f"{current_app.config['DATA_DIRECTORY']}/entries"), sep='\n')

    return 0


# Data is stored in human-readable format, but URLs and paths do not need spaces and uppercase letters.
def make_path(s: str):
    if s:
        return s.replace(' ', '_').lower()
    else:
        # If the string is a NoneType Object, prevent breakage by converting that to a string.
        # Such behavior is not ideal and the function should never receive a string with a null value.
        return "NULL"


def unmake_path(s: str):
    if s:
        return s.replace('_', ' ').title()
    else:
        return "NULL"


def configure_totp(current_user: Author, password: str):
    # Generate the secret seed for RFC 6238 2FA authentication
    shared_secret: str = pyotp.random_base32()
    totp = pyotp.TOTP(shared_secret, issuer=current_app.config['APP_URLS'][0])

    # Create the provisioning URI that will be used to generate a QR code.
    provisioning_uri = pyotp.totp.TOTP(shared_secret).provisioning_uri(
        name=current_user.username,
        issuer_name="Fang-CMS"
    )

    # Use the provisioning_uri to generate the qrcode and render it to the terminal for the user to scan it with their
    # TOTP-based Application. Also print out the TOTP seed for manual configuration if desired.
    qrcode = create_qrcode(provisioning_uri)
    click.echo("Scan this qrcode with your authenticator app.")
    qrcode.terminal(compact=True)
    click.echo(f"Or you can use the shared secret: {shared_secret}.")
    # Prompt the user for their generated OTP code and verify it matches the server.
    current_otp = input("Enter the 6-digit code supplied by your authenticator app: ")
    for count in range(0, 2):  # Exit-controlled loop
        # If able to verify the OTP code, encrypt the shared secret and store it in the database.
        if password is not None and totp.verify(current_otp):
            click.echo("Successfully added TOTP to your account.")
            encrypted_secret: TOTPSecret = encrypt(shared_secret, password)
            del shared_secret  # Delete the unencrypted form of the shared_secret as soon as it is encrypted.
            encrypted_secret.author_id = current_user.id
            svg_path = f"{current_app.config['DATA_DIRECTORY']}/authors/{current_user.username}.totp_qrcode.svg"
            qrcode.save(svg_path)
            db.session.add(encrypted_secret)
            db.session.commit()
            break
        # If the password is never initialized to a non-null value, throw an exception. Should never happen though...
        elif password is None:
            raise (TypeError("Unhandled Exception: Password cannot be a NoneType object."))
        elif count == 2:
            click.echo("Unable to verify TOTP method. Exiting now.", file=sys.stderr)

        return 0
