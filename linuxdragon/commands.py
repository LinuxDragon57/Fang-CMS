import click
import re
from flask.cli import with_appcontext
from getpass import getpass
from werkzeug.security import generate_password_hash

from linuxdragon.Models import db, Author


@click.command('create-tables')
@with_appcontext
def create_tables():
    db.create_all()


@click.command('create-admin')
@with_appcontext
def create_admin():
    username = input('Enter new username: ')
    password = getpass(prompt='Enter a password for the new user: ', stream=None)
    first_name = input("Enter author's first name: ")
    last_name = input("Enter author's last name: ")
    error = None

    # auth_criteria = re.compile(r'[.\S]   {8,50}')  # Match a string 8 to 50 characters with no whitespace.
    # name_criteria = re.compile(r'[a-zA-Z]{1,26}')  # Match strings of 1 to 26 letters.
    # input_check = [
    #    auth_criteria.match(username),
    #    auth_criteria.match(password),
    #    name_criteria.match(first_name),
    #    name_criteria.match(last_name)
    #    ]

    # for criterion in input_check:
    #    if criterion is None:
    #        error = "Missing or Invalid required arguments. Whitespace isn't allowed."

    if error is None:
        try:
            if Author.query.filter_by(username=username).first() is None:
                admin = Author(
                    username=username,
                    passwd_hash=generate_password_hash(password),
                    first_name=first_name,
                    last_name=last_name,
                    admin=True
                )
                db.session.add(admin)
                db.session.commit()
                error = f"Successfully added {username} as an Admin."
            else:
                raise ValueError('DBIntegrityError: ')
        except ValueError as err:
            error = f"{err} {username} is already registered."

    print(error)
