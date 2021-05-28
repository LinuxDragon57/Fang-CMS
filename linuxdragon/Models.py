from datetime import datetime
import peewee

db = peewee.SqliteDatabase('test.db')


class BaseModel(peewee.Model):
    # A base model that will use our database
    class Meta:
        database = db


class Author(BaseModel):
    userID = peewee.IntegerField(primary_key=True)
    username = peewee.CharField(unique=True, null=False)
    passwd_hash = peewee.CharField(null=False)
    f_name = peewee.CharField(null=False)
    l_name = peewee.CharField(null=False)
    admin = peewee.BooleanField(null=False, default=False)


class Entry(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    title = peewee.CharField(null=False)
    content = peewee.TextField(null=False)
    created_on = peewee.DateTimeField(default=datetime.now, null=False)
    genre = peewee.CharField(null=False)


class AuthorEntries(BaseModel):
    author = peewee.ForeignKeyField(Author, backref='blogposts')
    posts = peewee.ForeignKeyField(Entry, backref='created_by')
