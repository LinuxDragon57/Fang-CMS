import os
import sys
from secrets import compare_digest

import click
import re
from flask.cli import with_appcontext
from getpass import getpass
from werkzeug.security import generate_password_hash
from flask import current_app

from linuxdragon.Models import db, Author


@click.command('init-db')
@with_appcontext
def initialize_database():
    db.create_all()


def create_author(is_admin: bool):
    username = input('Enter new username: ')
    while True:
        password = getpass(prompt='Enter a password for the new user: ', stream=None)
        repeated_password = getpass(prompt='Repeat the password:', stream=None)
        if not compare_digest(password, repeated_password):
            print('Error: Passwords do not match. Please try again.', file=sys.stderr)
        else:
            break

    first_name = input("Enter author's first name: ")
    last_name = input("Enter author's last name: ")
    error = None

    auth_criteria = re.compile(r'^[\S]{8,50}$')  # Match a string of 8 to 50 whitespace-free characters.
    name_criteria = re.compile(r'^[a-z A-Z.]{1,26}$')  # Match strings up to 26 letters, periods, or spaces.
    input_check = [
        auth_criteria.match(username),
        auth_criteria.match(password),
        name_criteria.match(first_name),
        name_criteria.match(last_name)
    ]

    for criterion in input_check:
        if criterion is None:
            error = """
            Invalid arguments or missing requirements:
                ~ Whitespace isn't allowed.
                ~ The password and username must be at least 8 characters long.
                ~ Name fields can only contain letters.
                ~ Empty strings aren't allowed.
            """

    if error is None:
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
                    error = f"Successfully added {username} as an Admin."
                elif is_admin is False:
                    error = f"Successfully added {username}."
            else:
                raise ValueError('DBIntegrityError: ')
        except ValueError as err:
            error = f"{err} {username} is already registered."

    print(error)


@click.command('create-admin')
@with_appcontext
def create_admin():
    create_author(True)


@click.command('create-user')
@with_appcontext
def create_user():
    create_author(False)


@click.command('mkdatadirs')
@with_appcontext
def initialize_data_directories():
    if not os.path.isdir(current_app.config['DATA_DIRECTORY']):
        os.mkdir(current_app.config['DATA_DIRECTORY'])
        print(f"Created the data directory at {current_app.config['DATA_DIRECTORY']}")
    else:
        print(f"The data directory already exists with the current config.")

    for genre in current_app.config['GENRES']:
        genre = mkpath(genre)
        if not os.path.isdir(f"{current_app.config['DATA_DIRECTORY']}/{genre}"):
            os.mkdir(f"{current_app.config['DATA_DIRECTORY']}/{genre}")
            print(f"Created directory: {current_app.config['DATA_DIRECTORY']}/{genre}")
        else:
            print(f"{current_app.config['DATA_DIRECTORY']}/{genre} already exists.")


def mkpath(s: str):
    return s.replace(' ', '_').lower()
