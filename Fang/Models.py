from datetime import date
from secrets import token_urlsafe, randbits
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func

db = SQLAlchemy()


# Using Flask-SQLAlchemy, each Class represents an SQL Table.
class Author(db.Model):
    id = db.Column(db.SmallInteger, primary_key=True, default=randbits(12))
    username = db.Column(db.String(50), unique=True, nullable=False)
    passwd_hash = db.Column(db.CHAR(102), unique=True, nullable=False)
    first_name = db.Column(db.String(26), unique=False, nullable=False)
    last_name = db.Column(db.String(26), unique=False, nullable=False)
    admin = db.Column(db.Boolean(), default=False)
    totp_secret = db.relationship('TOTPSecret', uselist=False, backref='author')
    entries = db.relationship('Entry', backref='author', lazy=True)

    def __repr__(self):
        return f"<Author '{self.username}'>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# Table is a one-to-many relationship, and stores Metadata for each Author's entries.
class Entry(db.Model):
    id = db.Column(db.CHAR(16), primary_key=True, default=token_urlsafe)
    title = db.Column(db.String(25), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    genre = db.Column(db.String(25), nullable=False)
    content_path = db.Column(db.Text(), nullable=False)
    date_created = db.Column(db.Date(), default=date.today())
    last_update = db.Column(db.Date(), onupdate=date.today())
    author_id = db.Column(db.SmallInteger, db.ForeignKey('author.id'))

    def __repr__(self):
        return f"<Entry '{self.title}'>"

    @hybrid_property
    def genre_url(self):
        return self.genre.replace(' ', '_').lower()

    @genre_url.expression
    def genre_url(self):
        return func.lower(func.replace(self.genre, ' ', '_'))

    @hybrid_property
    def title_url(self):
        return self.title.replace(' ', '_').lower()

    @title_url.expression
    def title_url(self):
        return func.lower(func.replace(self.title, ' ', '_'))

    @hybrid_property
    def created_on(self):
        return self.date_created.strftime("%A, %d %B %Y")

    @created_on.expression
    def created_on(self):
        return func.strftime(self.date_created, "%A, %d %B %Y")

    @hybrid_property
    def updated_on(self):
        return self.last_update.strftime("%A, %d %B %Y")

    @updated_on.expression
    def updated_on(self):
        return func.strftime(self.last_update, "%A, %d %B %Y")


# Table is a one-to-one relationship, and stores the encryption information for each author's TOTP Seed.
class TOTPSecret(db.Model):
    author_id = db.Column(db.SmallInteger, db.ForeignKey('author.id'), primary_key=True)
    salt = db.Column(db.String(), nullable=False)
    cipher_text = db.Column(db.String(), nullable=False)
    nonce = db.Column(db.String(), nullable=False)
    tag = db.Column(db.String(), nullable=False)
    
    def __repr__(self):
        return f"<{Author.query.get(self.author_id).username} TOTP Seed>"
    