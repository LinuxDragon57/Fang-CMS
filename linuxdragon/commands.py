import os
import sys
import click
import re
from secrets import compare_digest
from flask.cli import with_appcontext
from getpass import getpass
from werkzeug.security import generate_password_hash
from flask import current_app

from linuxdragon.Models import db, Author
from linuxdragon.security import configure_totp


# Function allows the user to initialize the database with a simple Flask command.
# It merely makes a call to the db object in the application's SQLAlchemy Models.
@click.command('init-db')
@with_appcontext
def initialize_database():
    db.create_all()


def create_author(is_admin: bool):
    # Prompt the user to create a new username
    username = input('Enter new username: ')
    while True:  # Exit-controlled loop that exits when the user is able to successfully enter the same password twice.
        password = getpass(prompt='Enter a password for the new user: ', stream=None)
        repeated_password = getpass(prompt='Repeat the password:', stream=None)
        # Use secrets.compare_digest to ensure that the user was able to enter the same password twice.
        if not compare_digest(password, repeated_password):
            print('Error: Passwords do not match. Please try again.', file=sys.stderr)
        else:
            break

    # Prompt for the new user's full name.
    first_name = input("Enter author's first name: ")
    last_name = input("Enter author's last name: ")
    error = None

    auth_criteria = re.compile(r'^\S{8,50}$')  # Match a string of 8 to 50 whitespace-free characters.
    name_criteria = re.compile(r'^[a-z A-Z.]{1,26}$')  # Match strings up to 26 letters, periods, or spaces.
    # Using python's regex library, scrub the data to ensure it doesn't break the database and ensure it makes sense.
    input_check = [
        auth_criteria.match(username),
        auth_criteria.match(password),
        name_criteria.match(first_name),
        name_criteria.match(last_name)
    ]

    # If anything fails the regex check, set the error variable to the following verbose string.
    for criterion in input_check:
        if criterion is None:
            error = \
                """
                Invalid arguments or missing requirements:
                    ~ Whitespace isn't allowed.
                    ~ The password and username must be at least 8 characters long.
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
                    admin=is_admin
                )
                db.session.add(user)
                db.session.commit()
                if is_admin is True:
                    print(f"Successfully added {username} as an Admin.")
                elif is_admin is False:
                    print(f"Successfully added {username}.")

                totp_prompt = input("Would you like to set up TOTP? Y/n (Default: Y): ")
                if totp_prompt.lower() != 'n':
                    configure_totp(user)
            else:
                raise ValueError('DBIntegrityError: ')
        except ValueError as err:
            error = f"{err} {username} is already registered."

    if error:
        print(error)


# Function allows the user to create an administrator account with a Flask command.
@click.command('create-admin')
@with_appcontext
def create_admin():
    create_author(True)


# Function allows the user to create an unprivileged account with a Flask command.
@click.command('create-user')
@with_appcontext
def create_user():
    create_author(False)


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

    # Iterate through the available "GENRES" defined in the TOML file
    # and create directories for them if they do not exist
    for genre in current_app.config['GENRES']:
        genre_path = f"{current_app.config['DATA_DIRECTORY']}/entries/{mkpath(genre)}"
        if not os.path.isdir(genre_path):
            os.mkdir(genre_path)

    # Notify the user of success at completion of the function.
    print(f"\nSuccessfully created the paths at {current_app.config['DATA_DIRECTORY']}/entries:")
    print(*os.listdir(f"{current_app.config['DATA_DIRECTORY']}/entries"), sep='\n')


# Data is stored in human-readable format, but URLs and paths do not need spaces and uppercase letters.
def mkpath(s: str):
    if s:
        return s.replace(' ', '_').lower()
    else:
        return "NULL"
