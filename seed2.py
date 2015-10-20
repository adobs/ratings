from model import db, User, Movie, Rating, connect_to_db
from server import app

# connect_to_db(app)

def seed_user_data(filename):

    #empty Users table before adding seed data


    log_file = open(filename)

    for line in log_file:
        data = line.strip().split("|") #data is a list

        id = int(data[0])
        age = int(data[1])
        zip = data[4]

        new_user = User(user_id=id, age=age, zipcode=zip)
        db.session.add(new_user)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    db.session.query(User).delete()
    db.session.commit()
    seed_user_data("seed_data/u.user")