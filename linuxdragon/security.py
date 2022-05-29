import hashlib
import re
from base64 import b64encode, b64decode
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from werkzeug.security import generate_password_hash

from linuxdragon.Models import db, TOTPSecret, Author


def encrypt(plain_text: str, passwd: str):
    # generate a random salt
    salt = get_random_bytes(AES.block_size)

    # use the Scrypt KDF to get a private key from the password
    private_key = hashlib.scrypt(
        passwd.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32
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
        passwd.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32
    )

    # create the cipher config
    cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

    # decrypt the cipher text
    return cipher.decrypt_and_verify(cipher_text, tag)


def change_password(old_password: str, new_password: str, current_user: Author):
    current_user.passwd_hash = generate_password_hash(new_password)
    if current_user.totp_secret is not None:
        shared_secret: str = str(decrypt(current_user.totp_secret, old_password))
        encrypted_secret: TOTPSecret = encrypt(shared_secret, new_password)
        del shared_secret
        encrypted_secret.author_id = current_user.id
        db.session.delete(current_user.totp_secret)
        db.session.add(encrypted_secret)


def scrub_input_data(username: str, password: str, first_name: str, last_name:str):
    error: bool = False
    username_criteria = re.compile(r'^\S{8,64}$')  # Match a string of 8 to 64 whitespace-free characters.
    password_criteria = re.compile(r'^\S{32,256}$')  # Match a string of 32 to 256 whitespace-free characters.
    name_criteria = re.compile(r'^[a-z A-Z.]{1,32}$')  # Match a string of up to 26 letters, periods, or spaces.

    # Using Python's regex library, scrub the data to ensure it doesn't break the database.
    input_check = [
        username_criteria.match(username),
        password_criteria.match(password),
        name_criteria.match(first_name),
        name_criteria.match(last_name)
    ]

    # If anything fails the regex check, set the error boolean value to true.
    if not any(input_check):
        error = True

    return error
