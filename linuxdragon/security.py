import hashlib
import pyotp
import sys
from getpass import getpass
from base64 import b64encode, b64decode
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from segno import make as create_qrcode
from werkzeug.security import check_password_hash
from flask import current_app

from linuxdragon.Models import db, TOTPSecret, Author


def encrypt(plain_text: str, passwd: str):
    # generate a random salt
    salt = get_random_bytes(AES.block_size)

    # use the Scrypt KDF to get a private key from the password
    private_key = hashlib.scrypt(
        passwd.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32
    )

    # create cipher config
    cipher_config = AES.new(private_key, AES.MODE_GCM)

    # return a dictionary with the encrypted text
    cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))

    return TOTPSecret(
        salt=b64encode(salt).decode('utf-8'),
        cipher_text=b64encode(cipher_text).decode('utf-8'),
        nonce=b64encode(cipher_config.nonce).decode('utf-8'),
        tag=b64encode(tag).decode('utf-8')
    )


def decrypt(encrypted_secret: TOTPSecret, passwd: str):
    # decode the TOTPSecret entries from base64
    salt = b64decode(encrypted_secret.salt)
    cipher_text = b64decode(encrypted_secret.cipher_text)
    nonce = b64decode(encrypted_secret.nonce)
    tag = b64decode(encrypted_secret.tag)

    # generate the private key from the password and salt
    private_key = hashlib.scrypt(
        passwd.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32
    )

    # create the cipher config
    cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

    # decrypt the cipher text
    return cipher.decrypt_and_verify(cipher_text, tag)


def configure_totp(current_user: Author = None):
    # Ensure password always has a value by setting it to a default value of None.
    password = None
    # If no parameter is passed in, prompt for login credentials to retrieve the appropriate row in the Author database.
    if current_user is None:
        for count in range(0, 2):  # An exit-controlled loop.
            # Get the user's username and password, then query the database for a row matching the username.
            username = input('Enter your username: ')
            password = getpass(prompt='Enter your password: ', stream=None)
            current_user = Author.query.filter_by(username=username).one_or_none()

            # If the database returns a Null value - meaning that a user with the specified username does not exist,
            # then notify the user. Else if the password entered by the user is incorrect, notify the user. Else if
            # the maximum tries for authentication has been reached, raise a StopIteration error and exit the program.
            # Else exit the loop.
            if not current_user:
                print("Error: No matching username was found in the database. Please try again.")
            elif not check_password_hash(current_user.passwd_hash, password):
                print("Error: Incorrect password. Please try again.")
            elif count == 2:
                raise StopIteration("Error: Failed to authenticate after three tries. Exiting now.")
            else:
                break
    # If a parameter has been passed into the function, only prompt the user for their password.
    else:
        for count in range(0, 2):  # An exit-controlled loop.
            # Prompt the user to reenter their password.
            password = getpass(prompt='Please reauthenticate with your password: ', stream=None)
            # If the supplied password doesn't match the database's hashed value, notify the user. Else if the maximum
            # tries for authentication has been reached, raise a StopIteration error and exit the program.
            # Else exit the loop.
            if not check_password_hash(current_user.passwd_hash, password):
                print("Error: Incorrect password. Please try again.")
            elif count == 2:
                raise StopIteration("Error: Failed to authenticate after three tries. Exiting now.")
            else:
                break

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
    print("Scan this qrcode with your authenticator app.")
    qrcode.terminal(compact=True)
    print(f"Or you can use the shared secret: {shared_secret}.")
    # Prompt the user for their generated OTP code and verify it matches the server.
    current_otp = input("Enter the 6-digit code supplied by your authenticator app: ")
    for count in range(0, 2):   # Exit-controlled loop
        # If able to verify the OTP code, encrypt the shared secret and store it in the database.
        if password is not None and totp.verify(current_otp):
            print("Successfully added TOTP to your account.")
            encrypted_secret: TOTPSecret = encrypt(shared_secret, password)
            del shared_secret  # Delete the unencrypted form of the shared_secret as soon as it is encrypted.
            encrypted_secret.author_id = current_user.id
            db.session.add(encrypted_secret)
            db.session.commit()
            break
        # If the password is never initialized to a non-null value, throw an exception. Should never happen though...
        elif password is None:
            raise(TypeError("Unhandled Exception: Password cannot be a NoneType object."))
        elif count == 2:
            print("Unable to verify TOTP method. Exiting now.", file=sys.stderr)
