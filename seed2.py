from model import db, User, Movie, Rating

def seed_user_data(filename):
    log_file = open(filename)
    users = []

    for line in log_file:
        data = line.strip().split("|") #data is a list

        id = int(data[0])
        age = int(data[1])
        zip = data[4]

        new_user = User(user_id=id, age=age, zipcode=zip)
        db.session.add(new_user)

    db.session.commit()

