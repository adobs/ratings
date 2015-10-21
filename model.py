"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "Users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(32), nullable=True)
    lname = db.Column(db.String(32), nullable=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Movie(db.Model):
    """Movie table"""

    __tablename__ = "Movies"

    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        repr_string = "<Movie movie_id={id}, title={title}, released_at={date}, imdb_url={url}>"
        return repr_string.format(id=self.movie_id, 
                                  title=self.title, 
                                  date=self.released_at, 
                                  url=self.imdb_url)

class Rating(db.Model):
    """Ratings table"""

    __tablename__ = "Ratings"

    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("Movies.movie_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    movie = db.relationship('Movie',
                            backref=db.backref("ratings"), order_by=desc(score))
    user = db.relationship("User", 
                           backref=db.backref("ratings"), order_by=desc(score))

    def __repr__(self):
        """Provide helpful representation when printed."""

        repr_string = "<Rating rating_id={id}, movie_id={movie}, user_id={user}, score={score}>"
        return repr_string.format(id=self.rating_id,
                                  movie=self.movie_id,
                                  user=self.user_id,
                                  score=self.score)

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
