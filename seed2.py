from model import db, User, Movie, Rating, connect_to_db
from server import app
from datetime import datetime


def seed_user_data(filename):
    """Adds user data to database"""

    log_file = open(filename)

    for line in log_file:
        data = line.strip().split("|") #data is a list

        id = int(data[0])
        age = int(data[1])
        zip = data[4]

        new_user = User(user_id=id, age=age, zipcode=zip)
        db.session.add(new_user)

    db.session.commit()


def seed_movie_data(filename):
    """Adds movie data to database"""

    log_file = open(filename)

    for line in log_file:
        data = line.strip().split("|")

        #get data from split line
        id = int(data[0])
        title = data[1]
        release = data[2]
        url = data[4]

        #if there's a date there, parse it
        if release:
            release = datetime.strptime(data[2], "%d-%b-%Y")
        #otherwise, set release to None so it will become NULL in the database
        else:
            release = None

        #create a new record and add it to the queue
        new_movie = Movie(movie_id=id, title=title, 
                          released_at=release, imdb_url=url)
        db.session.add(new_movie)

    #commit changes
    db.session.commit()

def seed_rating_data(filename):
    """Adds rating data to database"""

    log_file = open(filename)

    for line in log_file:
        data = line.strip().split("\t")

        user_id = data[0]
        movie_id = data[1]
        score = data[2]

        new_rating = Rating(movie_id=movie_id, user_id=user_id, score=score)

        db.session.add(new_rating)

    db.session.commit()




if __name__ == "__main__":
    #connect db to app
    connect_to_db(app)

    #empty tables
    db.session.query(User).delete()
    db.session.query(Movie).delete()
    db.session.query(Rating).delete()
    db.session.commit()

    #seed data
    seed_user_data("seed_data/u.user")
    seed_movie_data("seed_data/u.item")
    seed_rating_data("seed_data/u.data")