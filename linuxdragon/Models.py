from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func

db = SQLAlchemy()


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    passwd_hash = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(26), unique=False, nullable=False)
    last_name = db.Column(db.String(26), unique=False, nullable=False)
    admin = db.Column(db.Boolean(), default=False)
    entries = db.relationship('Entry', backref='author', lazy=True)

    def __repr__(self):
        return f"<Author '{self.username}'>"

    def __init__(self, username, passwd_hash, first_name, last_name, admin):
        self.username = username
        self.passwd_hash = passwd_hash
        self.first_name = first_name
        self.last_name = last_name
        self.admin = admin

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    genre = db.Column(db.String(25), nullable=False)
    content_path = db.Column(db.Text(), nullable=False)
    date_created = db.Column(db.DateTime(), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __repr__(self):
        return f"<Entry '{self.title}'>"

    def __init__(self, title, description, genre, content_path, author_id):
        self.title = title
        self.description = description
        self.genre = genre
        self.content_path = content_path
        self.date_created = datetime.today()
        self.author_id = author_id

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
    def format_date(self):
        return self.date_created.strftime("%A, %d %B %Y")

    @format_date.expression
    def format_date(self):
        return func.strftime(self.date_created, "%A, %d %B %Y")
