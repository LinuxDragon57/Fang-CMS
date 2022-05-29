import os
import sys
import click
import pyotp

from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from segno import make as create_qrcode

from linuxdragon.Models import db, Author, TOTPSecret
from linuxdragon.security import encrypt, change_password, scrub_input_data


# Function allows the user to initialize the database with a simple Flask command.
# It merely makes a call to the db object in the application's SQLAlchemy Models.
@click.command('init-db')
@with_appcontext
def initialize_database():
    db.create_all()


@click.command()
@click.password_option()
def cli_login(password: str):
    for count in range(0, 2):  # An exit-controlled loop.
        # Get the user's username and password, then query the database for a row matching the username.
        username = click.prompt("Username: ")
        password = password
        current_user: Author = Author.query.filter_by(username=username).one_or_none()

        # If the database returns a Null value - meaning that a user with the specified username does not exist,
        # then notify the user. Else if the password entered by the user is incorrect, notify the user. Else if
        # the maximum tries for authentication has been reached, raise a StopIteration error and exit the program.
        # Else exit the loop and return the collected variable values.
        if not current_user:
            click.echo("Error: No matching username was found in the database. Please try again.", file=sys.stderr)
        elif not check_password_hash(current_user.passwd_hash, password):
            click.echo("Error: Incorrect password. Please try again.", file=sys.stderr)
        elif count == 2:
            raise StopIteration("Error: Failed to authenticate after three tries. Exiting now.")
        else:
            return current_user, password


@click.command('create-author')
@click.option('--username', prompt=True)
@click.password_option()
@click.option('--admin', is_flag=True)
@with_appcontext
def create_author(username: str, password: str, admin: bool):
    # Prompt for the new user's username, password, and full name.
    first_name = click.prompt("Enter author's first name ", type=str)
    last_name = click.prompt("Enter author's last name ", type=str)
    error = None

    if scrub_input_data(username, password, first_name, last_name):
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

                totp_prompt = click.confirm("Would you like to set up TOTP? ")
                if totp_prompt:
                    configure_totp(user, password)
        except ValueError as err:
            error = f"{err} {username} is already registered."

    if error:
        click.echo(error, file=sys.stderr)


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


# A function that allows the user to set up TOTP directly with a Flask command.
@click.command('configure-totp')
@with_appcontext
def set_up_totp():
    configure_totp()


@click.command('mkdatadirs')
@with_appcontext
def initialize_data_directories():
    # If the "DATA_DIRECTORY" specified in the TOML file doesn't exist, create it.
    if not os.path.isdir(current_app.config['DATA_DIRECTORY']):
        os.mkdir(current_app.config['DATA_DIRECTORY'])

    # If the "entries" directory doesn't exist, create it.
    if not os.path.isdir(f"{current_app.config['DATA_DIRECTORY']}/entries"):
        os.mkdir(f"{current_app.config['DATA_DIRECTORY']}/entries")

    # Same thing for the "authors" directories.
    if not os.path.isdir(f"{current_app.config['DATA_DIRECTORY']}/authors"):
        os.mkdir(f"{current_app.config['DATA_DIRECTORY']}/authors")

    # Iterate through the available "GENRES" defined in the TOML file
    # and create directories for them if they do not exist
    for genre in current_app.config['GENRES']:
        genre_path = f"{current_app.config['DATA_DIRECTORY']}/entries/{mkpath(genre)}"
        if not os.path.isdir(genre_path):
            os.mkdir(genre_path)

    for author in Author.query.all():
        if not os.path.isdir(f"{current_app.config['DATA_DIRECTORY']}/authors/{author.username}"):
            os.mkdir(f"{current_app.config['DATA_DIRECTORY']}/authors/{author.username}")

    # Notify the user of success at completion of the function.
    print(f"\nSuccessfully created the paths at {current_app.config['DATA_DIRECTORY']}/entries:")
    print(*os.listdir(f"{current_app.config['DATA_DIRECTORY']}/entries"), sep='\n')


# Data is stored in human-readable format, but URLs and paths do not need spaces and uppercase letters.
def mkpath(s: str):
    if s:
        return s.replace(' ', '_').lower()
    else:
        return "NULL"


def configure_totp(current_user: Author = None, password=None):
    # If no parameter is passed in, prompt for login credentials to retrieve the appropriate row in the Author database.
    if current_user is None:
        # If a parameter has been passed into the function, only prompt the user for their password.
        current_user, password = cli_login()
    elif current_user and not password:
        raise (TypeError("Unhandled Exception: Password cannot be a NoneType object."))

    # Generate the secret seed for RFC 6238 2FA authentication
    shared_secret = pyotp.random_base32()
    totp = pyotp.TOTP(shared_secret)

    # Create the provisioning URI that will be used to generate a QR code.
    provisioning_uri = pyotp.totp.TOTP(shared_secret).provisioning_uri(
        name=current_user.username,
        issuer_name=current_app.config['APP_URI']
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
