from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Link between the SQLAlchemy structure in Python and the SQLite structure
    """

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class User(db.Model):
    """
    Represents a user table.
    id is the primary key
    Another column contains the user’s name
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class Movie(db.Model):
    """
    Represents a films table
    the primary key is id
    other columns:
        movie title as title
        director
        year of release as publication_year
        movie cover as poster_url for display in the frontend
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    director = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    poster_url = db.Column(db.String)

class UserMovie(db.Model):
    """
    represents the user-movie table
    serves as a join table for a many-to-many relationship between users and movies
    """

    # ondelete='CASCADE' wenn ein User gelöscht wird werden automatisch alle seine zugehörigen Einträge aus der UserMovie Tabelle gelöscht.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), primary_key=True)