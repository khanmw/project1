from flask import Flask, redirect, url_for, render_template, request, session, g, abort
from datetime import timedelta
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json

app = Flask(__name__)
app.secret_key = "secretive"
app.permanent_session_lifetime = timedelta(minutes=5)

DATABASE_URL = "postgres://uqomdazskmxxsr:db2a79e862a3e486ceb8c5b8905ccf5cf9f65931a583e1945d13acdc8bc8dca4@ec2-34-202-7-83.compute-1.amazonaws.com:5432/ddcuv1vgb1p4op"
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home", methods=["POST", "GET"])
def home():
    if "login_user" not in session:
        return render_template("login.html", message="Please Login First", work="Login")
    user = session["login_user"]

#   Search-specific book
    if request.method == "POST":
        search = "%"+request.form["search"].strip().upper()+"%"
        search_result = db.execute("SELECT * FROM books WHERE UPPER(CONCAT(isbn,title,author)) LIKE :search ORDER BY title",
                               {"search": search}).fetchall()
        return render_template('home.html',user=user,book_list=search_result)

#   1st Ten Books
    else:
        book_list = db.execute("SELECT isbn, title, author, year FROM books").fetchall()[:10]
        return render_template("home.html", user=user, book_list=book_list)

@app.route("/bookpage/<string:isbn>", methods=['GET', 'POST'])
def bookpage(isbn):
    if "login_user" not in session:
        return render_template("login.html", message="Please Login", work="Login")
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    user = session["login_user"]
    if request.method == "POST":
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        if db.execute("SELECT * FROM reviews WHERE username = :user AND isbn = :isbn",{"user": user, "isbn": isbn}).fetchone() is None:
            db.execute("INSERT INTO reviews (isbn, review, rating, username) VALUES (:isbn,:review,:rating,:user)",{"isbn": isbn, "review": comment, "rating": rating, "user": user})
        else:
            db.execute("UPDATE reviews SET review = :comment, rating = :rating WHERE username = :user AND isbn = :isbn",
                {"isbn": isbn,"comment": comment, "rating": rating, "user": user})
        db.commit()
#   Goodreads pull
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "4VzA6u4V4UR42pFv3OfqA", "isbns": book.isbn}).json()["books"][0]
    ratings_count = res["ratings_count"]
    average_rating = res["average_rating"]

#   Existing Reviews
    reviews = db.execute("SELECT username, rating, review FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    return render_template("bookpage.html", user=user, book=book, ratings_count=ratings_count,average_rating=average_rating,username=user,reviews=reviews)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.pop("username", None)
        #		session.permanent = True
        login_user = request.form["login_user"]
        session["login_user"] = login_user
        login_password = request.form["login_password"]
        session["login_password"] = login_password
        data = db.execute("SELECT username, password FROM users").fetchall()
        if login_user == "" or login_password == "":
            return render_template('login.html', message="Blank userid and/or password")
        else:
            for i in range(len(data)):
                if data[i]["username"] == login_user and data[i]["password"] == login_password:
                    session["username"] = data[i]["username"]
                    return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        register_user = request.form["register_user"]
        session["register_user"] = register_user
        register_password = request.form["register_password"]
        session["register_password"] = register_password
        register_password2 = request.form["register_password2"]
        session["register_password2"] = register_password2
        data = db.execute("SELECT username FROM users").fetchall()
        for i in range(len(data)):
            if data[i]["username"] == register_user:
                return render_template('register.html', message="Username already exist")
        if register_user == "" or register_password == "" or register_password != register_password2:
            return render_template('register.html',message="Userid/password was blank or password reentry mismatched")
        else:
            db.execute('INSERT INTO users (username,password) VALUES (:a,:b)',
                       {'a': register_user, 'b': register_password})
        db.commit()
        return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    query_attributes = ["isbn", "title", "author","year","rating_counts","avg_ratings"]
    query = db.execute("SELECT books.*, COUNT(reviews.rating) AS rating_counts, TO_CHAR(AVG(reviews.rating),'0.9') AS avg_ratings FROM books LEFT JOIN reviews ON books.isbn=reviews.isbn WHERE books.isbn = :isbn GROUP BY 1", {"isbn": isbn}).fetchone()
    if query is None:
        return render_template("api.html", message="Invalid ISBN. Please retry")
    query_dict = dict(zip(query_attributes, query))
    json_query = json.dumps(query_dict)
    return render_template("api.html",result=json_query)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html",message="ISBN not found")

if __name__ == "__main__":
    app.run(debug=True)
