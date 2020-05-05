import os
import functools

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt

import project_tools
import goodreads_requests

app = Flask(__name__)
app.secret_key = 'some_secret'
Session(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def login_required(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if session.get("logged_in"):
            return func(*args, **kwargs)
        else:
            return render_template("message_for_user.html", title="Info", message="You must login first.")

    return wrap



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html",
                           message="Registration",
                           method="commit_register",
                           button_label="Register",
                           title="Register")


@app.route("/commit_register", methods=["POST"])
def commit_register():
    name = request.form.get("username")
    if db.execute("SELECT name FROM users WHERE name = :name", {"name": name}).rowcount == 1:
        return render_template("message_for_user.html",
                               title="Oops...",
                               message=f"User {name} already exists.")
    try:
        user_input_pw_hash = hash_pw(request.form.get("password"))
    except ValueError as v:
        return render_template("message_for_user.html", title="Error", message="Password is empty.")

    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name,
                                                                                "password": user_input_pw_hash})
    db.commit()
    return render_template("message_for_user.html", title="Success",
                           message="Thank you for your registration. Please log in to use our features.")


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html",
                           message="Welcome",
                           method="commit_login",
                           button_label="Sign In",
                           title="Login")


@app.route("/commit_login", methods=["POST"])
def commit_login():
    name = request.form.get("username")
    password = request.form.get("password")
    if not password:
        return render_template("message_for_user.html", title="Error", message="Password is empty.")

    if db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).rowcount == 0:
        return render_template("message_for_user.html", title="Oops..."
                               , message="User name not found. If you're new, consider registering to our site.")

    # returns sqlalchemy RowProxy
    db_pw_hash = db.execute("SELECT password FROM users WHERE name = :name", {"name": name}).fetchone()

    if check_pw(db_pw_hash["password"], password):
        session['user_id'] = db.execute("SELECT user_id FROM users WHERE name = :name", {"name": name}).fetchone()[0]
        session['username'] = name
        session['logged_in'] = True
        return render_template("message_for_user.html", title=f"Welcome {name}!",
                               message="Login successful. You can now search books and view your submitted reviews.")
    else:
        return render_template("message_for_user.html", title="Oops...",
                               message="Incorrect password.")


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.clear()
    flash("You have been successfully signed out.")
    return redirect(url_for('index'))


def check_pw(pw_hash: str, candidate: str) -> bool:
    bcrypt = Bcrypt(app)
    return bcrypt.check_password_hash(pw_hash, candidate)


def hash_pw(password: str) -> str:
    bcrypt = Bcrypt(app)
    # decode in because of Python 3
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    return pw_hash


@app.route("/search", methods=["GET"])
@project_tools.login_required
def search():
    search_results = []
    return render_template("search.html", search_results=search_results
                           , message="Search by (part of) ISBN, author or title.")


@app.route("/get_books", methods=["POST"])
def get_books():
    search_pattern = request.form.get("search")
    if not search_pattern:
        message = "Please enter (part of) ISBN, author or title."
        return render_template("search.html", search_results=[], message=message)

    select = "SELECT title, a.name, year, isbn " \
             "FROM book_details b JOIN authors a ON b.author_id=a.author_id " \
             "WHERE {} ILIKE '%{}%'"

    search_results = list()
    search_results += db.execute(select.format("isbn", search_pattern)).fetchall()
    search_results += db.execute(select.format("title", search_pattern)).fetchall()
    search_results += db.execute(select.format("a.name", search_pattern)).fetchall()

    if not search_results:
        return render_template("search.html", search_results=search_results,
                               result=f"No item found for {search_pattern}.")
    return render_template("search.html", search_results=search_results)


@app.route("/layout_books/<isbn>")
@project_tools.login_required
def layout_books(isbn):
    # set 'globally' to later use in submit_review
    session["isbn"] = isbn
    message = ""
    reviews = list()
    book_info = db.execute("SELECT title, a.name, year "
                           "FROM book_details b JOIN authors a ON b.author_id = a.author_id "
                           "WHERE b.isbn = :isbn", {"isbn": isbn}).fetchone()
    title, author, year = book_info
    goodreads_info = goodreads_requests.get_review_counts(isbn)[0]
    gr_average_rating, gr_number_ratings = goodreads_info['average_rating'], goodreads_info['work_ratings_count']
    # review results
    review_results = db.execute("SELECT u.name, r.title, r.text, r.rating "
                         "FROM reviews r JOIN users u on r.user_id = u.user_id "
                         "WHERE r.isbn = :isbn", {"isbn": isbn})
    if review_results.rowcount == 0:
        message = "No reviews yet, be the first to add one."
        average_score, review_count = 0.0, 0
    else:
        reviews = review_results.fetchall()
        review_count = review_results.rowcount
        average_score = sum(row[3] for row in reviews) / review_count

    return render_template("layout_books.html",
                           title=title,
                           author=author,
                           year=year,
                           isbn=isbn,
                           review_count=review_count,
                           average_rating=average_score,
                           gr_number_ratings=gr_number_ratings,
                           gr_average_rating=gr_average_rating,
                           message=message,
                           reviews=reviews)


@app.route("/add_review", methods=["POST"])
@project_tools.login_required
def add_review():
    return render_template("add_review.html")


@app.route("/submit_review", methods=["POST"])
@project_tools.login_required
def submit_review():
    title = request.form.get("title")
    rating = request.form.get("rating")
    review = request.form.get("review")

    if title is None or title.strip() == '':
        return render_template("message_for_user.html", title="Please add a title."
                               , message="Use back in your browser to return to form.")
    if rating is None or rating.strip() == '':
        return render_template("message_for_user.html", title="Please add a rating"
                               , message="Use back in your browser to return to form.")
    # TODO: allow user to edit the review.
    if db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND isbn = :isbn",
                  {"user_id": session["user_id"], "isbn": session["isbn"]}
                  ).rowcount == 0:

        db.execute("INSERT INTO reviews(user_id, isbn, title, text, rating) VALUES (:user_id, :isbn, :title, :review, :rating)",
                   {"user_id": int(session["user_id"]), "isbn": session["isbn"],
                    "title": title, "review": review, "rating": int(rating)})
        db.commit()
    else:
        return render_template("message_for_user.html", title="Info",
                               message="You already added a review for this book.")

    return render_template("message_for_user.html", title="Thank you {}!".format(session['username'])
                           , message="Your review has been added successfully.")


@app.route("/my_reviews", methods=["GET"])
@project_tools.login_required
def my_reviews():
    reviews = db.execute("SELECT r.title, r.text, r.rating, b.title, a.name, r.isbn FROM reviews r JOIN book_details b "
                         "ON r.isbn = b.isbn JOIN authors a ON a.author_id=b.author_id "
                         "WHERE user_id = :user_id", {"user_id": session["user_id"]}).fetchall()
    print(reviews)
    return render_template("my_reviews.html", reviews=reviews)


@app.route("/api/<string:isbn>", methods=["GET"])
@project_tools.login_required
def api(isbn: str):
    review_results = db.execute("SELECT b.title, a.name, b.year, b.isbn, r.title, r.rating "
                        "FROM book_details b JOIN authors a ON b.author_id=a.author_id "
                        "JOIN reviews r ON b.isbn=r.isbn "
                        "WHERE b.isbn= :isbn", {"isbn": isbn})

    if review_results.rowcount == 0:
        return f"ISBN {isbn} not found.", 404
    else:
        reviews = review_results.fetchall()
        title, author, year = reviews[0][:3]
        review_count = review_results.rowcount
        average_score = sum(row[5] for row in reviews) / review_count

    return jsonify(title=title,
                   author=author,
                   year=year,
                   isbn=isbn,
                   review_count=review_count,
                   average_score=average_score)
