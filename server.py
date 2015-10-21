"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from model import User, Rating, Movie, connect_to_db, db
from flask_debugtoolbar import DebugToolbarExtension

 
app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("home.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all() #users is a list
    return render_template("users.html", users=users)


@app.route("/registration")
def show_registration_form():

    return render_template("registration.html")



@app.route("/newuser", methods=["POST"])
# if user not in database:
#     go to login
# else flash you are already a user, please login
# go to login
def process_new_user():
    email = request.form.get("email")
    fname = request.form.get("fname")

    #check to see if the user is already registered
    #flash different message depending on that, and if they're new
    #add their info to the database
    if db.session.query(User).filter(User.email == email).first():
        msg = "Hi, {name}!  You are already registered with us.  Please log in."
        flash(msg.format(name=fname))
    else:
        msg = "Hi, {name}! You have successfully created an account. Please log in."
        flash(msg.format(name=fname))

        #get the rest of the user's info
        lname = request.form.get("lname")
        password = request.form.get("password")
        age = int(request.form.get("age"))
        zipcode = request.form.get("zipcode")

        #add user to the database
        new_user = User(fname=fname, lname=lname, email=email, age=age,
                        zipcode=zipcode, password=password)
        db.session.add(new_user)
        db.session.commit()

    return redirect("/login")

@app.route("/login")
def show_login_page():
    return "HI"

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()