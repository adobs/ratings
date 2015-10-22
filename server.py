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
    """Show the homepage"""

    return render_template("home.html")

@app.route("/users")
def user_list():
    """Show list of users"""

    users = User.query.all() #users is a list
    return render_template("users.html", users=users)


@app.route("/user/<int:user_id>")
def show_user_info(user_id):
    """Show info for a particular user"""

    user = db.session.query(User).filter(User.user_id == user_id).one()
    fname = user.fname
    lname = user.lname
    email = user.email
    age = user.age
    zipcode = user.zipcode
    ratings = (db.session.query(Movie.title, Rating.score)
                         .join(Rating)
                         .filter(Rating.user_id == user_id)
                         .all())

    return render_template("user-info.html", user_id=user_id, fname=fname,
                           lname=lname, email=email, age=age, zipcode=zipcode, 
                           ratings=ratings)

@app.route("/movies")
def movie_list():
    """Show list of movies"""

    movies = (db.session.query(Movie.title, Movie.movie_id)
                        .order_by(Movie.title)
                        .all())

    for title, movie_id in movies:
        title = title.encode("latin-1")
    return render_template("movies.html", movies=movies)


@app.route("/movie/<int:movie_id>")
def show_movie_info(movie_id):
    """Show info for a particular movie"""

    movie = db.session.query(Movie).filter(Movie.movie_id == movie_id).one()
    avg_rating = (db.session.query(db.func.avg(Rating.score))
                           .filter(Rating.movie_id == movie_id).one())[0]
    users_rating = (db.session.query(Rating.score)
                              .filter(Rating.user_id == 
                                      session.get("user_id", None))
                              .first())
    if users_rating:
        users_rating = users_rating[0]

    ratings = (db.session.query(User.user_id, Rating.score)
                         .join(Rating)
                         .filter(Rating.movie_id == movie_id)
                         .order_by(User.user_id)
                         .all())

    return render_template("movie-info.html", movie=movie,
                                              users_rating=users_rating, 
                                              avg_rating=avg_rating, 
                                              ratings=ratings)


@app.route("/registration")
def show_registration_form():
    """Show new user registration page"""

    return render_template("registration.html")


@app.route("/newuser", methods=["POST"])
def process_new_user():
    """Process user registration form"""

    #get info necessary to check if user is new
    email = request.form.get("email")
    fname = request.form.get("fname")

    #check to see if the user is already registered
    if db.session.query(User).filter(User.email == email).first():
        msg = "Hi, {name}!  You are already registered with us.  Please log in."
        flash(msg.format(name=fname))

    #if not, add user to database    
    else:
        msg = "Hi, {name}! You have successfully created an account. Please log in."
        flash(msg.format(name=fname))

        #get the rest of the user's info
        lname = request.form.get("lname")
        password = hash(request.form.get("password"))
        age = int(request.form.get("age"))
        zipcode = request.form.get("zipcode")

        #add user to the database
        new_user = User(fname=fname, lname=lname, email=email, age=age,
                        zipcode=zipcode, password=password)
        db.session.add(new_user)
        db.session.commit()

    #in either case, take the user to login page
    return redirect("/login")


@app.route("/login")
def show_login_page():
    """Show login page"""

    return render_template("login.html")


@app.route("/do-login", methods=["POST"])
def log_in():
    """Validate email and password"""

    #look up user in the database
    email = request.form.get("email")
    password = hash(request.form.get("password"))
    user = db.session.query(User).filter(User.email == email).first()

    #check if user is in our database
    if user is not None: #email was found

        #if found, check password against database
        if password == int(user.password): #success
            #get user's name
            fname = user.fname
            
            #TODO change navbar

            #add user to session
            session["user_id"] = user.user_id
            session["fname"] = fname

            #flash message and redirect to homepage
            message = "Welcome, {name}. You are successfully logged in."
            flash(message.format(name=fname))
            return redirect("/user/" + str(user.user_id))

        else: #wrong password
            flash("Incorrect password. Please try again.")
            return redirect("/login")

    else: #user not found in database
        flash("Email did not match a registered user. Please try again.")
        return redirect("/login")


@app.route("/logout")
def log_out():
    """Print goodbye message, clear session, and redirect to homepage"""
    
    #if there's a user logged in, clear the session and queue up a 
    #goodbye message to flash
    if session.get("user_id"):
        fname = session["fname"]
        message = "Goodbye, {name}!"
        session.clear()
        flash(message.format(name=fname))

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()