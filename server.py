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


################ MOVIE AND USER LISTS/INFO ROUTES ################


@app.route("/users")
def user_list():
    """Show list of users"""

    users = User.query.all() #users is a list
    return render_template("users.html", users=users)


@app.route("/user/<int:user_id>")
def show_user_info(user_id):
    """Show info for a particular user"""

    #get the user object out of the database and pull out all the info
    #it turns out we didn't need to pull out (d'oh!)
    user = db.session.query(User).filter(User.user_id == user_id).one()
    fname = user.fname
    lname = user.lname
    email = user.email
    age = user.age
    zipcode = user.zipcode

    #get all of the user's previous ratings
    ratings = (db.session.query(Movie.title, Rating.score)
                         .join(Rating)
                         .filter(Rating.user_id == user_id)
                         .all())

    #display user info page
    return render_template("user-info.html", user_id=user_id, fname=fname,
                           lname=lname, email=email, age=age, zipcode=zipcode, 
                           ratings=ratings)


@app.route("/movies")
def movie_list():
    """Show list of movies"""

    #get movie titles and id's out of the database
    movies = (db.session.query(Movie.title, Movie.movie_id)
                        .order_by(Movie.title)
                        .all())

    #deal with encoding (accented characters are the issue here)
    for title, movie_id in movies:
        title = title.encode("latin-1")

    #display movie list page
    return render_template("movies.html", movies=movies)


@app.route("/movie/<int:movie_id>")
def show_movie_info(movie_id):
    """Show info for a particular movie"""

    #retrieve the movie object given the movie id
    movie = db.session.query(Movie).filter(Movie.movie_id == movie_id).one()

    #calculate average rating
    avg_rating = (db.session.query(db.func.avg(Rating.score))
                           .filter(Rating.movie_id == movie_id).one())[0]

    #get user's previous rating, if any
    users_rating = (db.session.query(Rating.score)
                              .filter(Rating.user_id == 
                                      session.get("user_id", None))
                              .first())
    if users_rating:
        users_rating = users_rating[0]

    #get a list of all ratings for this movie
    ratings = (db.session.query(User.user_id, Rating.score)
                         .join(Rating)
                         .filter(Rating.movie_id == movie_id)
                         .order_by(User.user_id)
                         .all())

    #display the movie info page
    return render_template("movie-info.html", movie=movie,
                                              users_rating=users_rating, 
                                              avg_rating=avg_rating, 
                                              ratings=ratings)


############################ RATING ROUTES ############################


@app.route("/update-rating/<int:movie_id>", methods=["POST"])
def update_rating(movie_id):
    """Update logged-in user's rating of given movie"""

    #get the rating from the form
    score = request.form.get("rating")

    #retrieve the old rating record from the database
    old_rating_object = (db.session.query(Rating)
                                   .filter(Rating.user_id == 
                                           session["user_id"],
                                           Rating.movie_id == movie_id)
                                   .one())

    #update the rating
    old_rating_object.score = score

    #push the change to the database
    db.session.commit()

    #stay on the movie info page
    return redirect("/movie/" + str(movie_id))


@app.route("/rate/<int:movie_id>", methods=["POST"])
def rate_movie(movie_id):
    """Add logged-in user's rating for given movie"""
    
    #get the rating from the form
    score = request.form.get("rating")

    #create a new record and add it to the queue
    new_rating = Rating(movie_id=movie_id, user_id=session["user_id"], 
                        score=score)
    db.session.add(new_rating)

    #commit changes
    db.session.commit()

    #reload movie page including new rating
    return redirect("/movie/" + str(movie_id))


################ LOGIN, LOGOUT, AND REGISTRATION ROUTES ################


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

    #go back to the homepage
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()