from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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
        return '<Author %r>' % self.username


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(35), nullable=False)
    genre = db.Column(db.String(25), nullable=False)
    content_path = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __repr__(self):
        return '<Entry %r>' % self.title


# class AuthorEntries(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    author = db.Column(db.Integer, db.ForeignKey('author.id'))
#    posts = db.Column(db.Integer, db.ForeignKey('entry.id'))
