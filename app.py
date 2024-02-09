import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from django.contrib.auth.decorators import login_required

# Configure application
app = Flask(__name__)

# Configure login
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLite database
# db = SQL("sqlite:///familytree.db")
con = sqlite3.connect("familytree.db", check_same_thread=False)
db = con.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmation = request.form['confirmation']
        check_username = db.execute("SELECT username FROM users")
        for n in range(len(check_username)):
            if check_username[n].get("username") == username:
                return 'Unique name is required!', 400
        if not username:
            return 'Name is required!', 400
        elif not password:
            return 'Password is required!', 400
        elif not confirmation:
            return 'Password confirmation is required!', 400
        elif not password == confirmation:
            return 'Password should be equal to Password confirmation!', 400
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
            return render_template("login.html")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/tree")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/tree", methods=["GET", "POST"])
@login_required
def tree():
    if request.method == 'POST':
        search = request.form['search']
        if search == "":
            user_data = db.execute("SELECT * FROM person")
        if search != "":
            user_data = db.execute("SELECT * FROM person WHERE lastname LIKE ? OR name LIKE ?", search, search)
        return render_template("tree.html", user_data=user_data, search=search)
    else:
        user_data = db.execute("SELECT * FROM person")
        return render_template("tree.html", user_data=user_data)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        print(" add - ", name, lastname)
        birth_date = request.form['birth_date']
        birth_place = request.form['birth_place']
        death_date = request.form['death_date']
        death_place = request.form['death_place']
        print(" add - ", birth_date, birth_place, death_date, death_place)
        sex = request.form['sex']
        print(" add - ", sex)
        try:
            father_id = request.form['father_id']
        except:
            father_id = ""
        print(" add - ", father_id)
        try:
            mother_id = request.form['mother_id']
        except:
            mother_id = ""
        print(mother_id)
        db.execute("INSERT INTO person (name, lastname, birth_date, birth_place, death_date, death_place, sex) VALUES (?, ?, ?, ?, ?, ?, ?)", name, lastname, birth_date, birth_place, death_date, death_place, sex)
        person = db.execute("SELECT id FROM person WHERE name = ? AND lastname = ? AND birth_date = ? AND birth_place = ? AND death_date = ? AND death_place = ? AND sex = ?", name, lastname, birth_date, birth_place, death_date, death_place, sex)
        person_id = person[0]["id"]
        if mother_id != "" and father_id != "":
            db.execute("INSERT INTO parent (person_id, father_id, mother_id) VALUES (?, ?, ?)", person_id, father_id, mother_id)
        if mother_id != "" and father_id == "":
            db.execute("INSERT INTO parent (person_id, mother_id) VALUES (?, ?)", person_id, mother_id)
        if mother_id == "" and father_id != "":
            db.execute("INSERT INTO parent (person_id, father_id) VALUES (?, ?)", person_id, father_id)
        return redirect("/tree")
    else:
        man = db.execute("SELECT * FROM person WHERE sex = ?", 'male')
        woman = db.execute("SELECT * FROM person WHERE sex = ?", 'female')
        return render_template("add.html", man=man, woman=woman)


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == 'POST':
        person_id = request.form['person_id']
        name = request.form['name']
        # middlename = request.form['middlename']
        lastname = request.form['lastname']
        # print(name, middlename, lastname)
        birth_date = request.form['birth_date']
        birth_place = request.form['birth_place']
        death_date = request.form['death_date']
        death_place = request.form['death_place']
        # print(birth_date, birth_place, death_date, death_place)
        sex = request.form['sex']
        print(sex)
        try:
            father_id = request.form['father_id']
        except:
            father_id = ""
        print(father_id)
        try:
            mother_id = request.form['mother_id']
        except:
            mother_id = ""
        print(mother_id)
        db.execute("UPDATE person SET name = ?, lastname = ?, birth_date = ?, birth_place = ?, death_date = ?, death_place = ?, sex = ? WHERE id = ?", name, lastname, birth_date, birth_place, death_date, death_place, sex, person_id)
        parents_test = db.execute("SELECT * FROM parent WHERE person_id = ?", person_id)
        if len(parents_test) == 0:
            if mother_id != "" and father_id != "":
                db.execute("INSERT INTO parent (person_id, father_id, mother_id) VALUES (?, ?, ?)", person_id, father_id, mother_id)
            if mother_id != "" and father_id == "":
                db.execute("INSERT INTO parent (person_id, mother_id) VALUES (?, ?)", person_id, mother_id)
            if mother_id == "" and father_id != "":
                db.execute("INSERT INTO parent (person_id, father_id) VALUES (?, ?)", person_id, father_id)
        else:
            db.execute("UPDATE parent SET father_id = ?, mother_id = ? WHERE person_id = ?", father_id, mother_id, person_id)
        return redirect("/tree")
    else:
        person_id = request.args.get('person_id')
        person_data = db.execute("SELECT * FROM person WHERE id = ?", person_id)
        birth_date = person_data[0].get('birth_date')
        father = db.execute("SELECT * FROM parent JOIN person ON parent.father_id = person.id WHERE parent.person_id = ?", person_id)
        man = []
        if len(father) == 0:
            man = db.execute("SELECT * FROM person WHERE person.sex = ? and person.birth_date < ? ORDER BY ?", 'male', birth_date, 'birth_date')
        mother = db.execute("SELECT * FROM parent JOIN person ON parent.mother_id = person.id WHERE parent.person_id = ?", person_id)
        woman = []
        if len(mother) == 0:
            woman = db.execute("SELECT * FROM person WHERE person.sex = ? and person.birth_date < ? ORDER BY ?", 'female', birth_date, 'birth_date')
        return render_template("edit.html", person_data=person_data, father=father, mother=mother, man=man, woman=woman, person_id=person_id)



@app.route("/details")
@login_required
def details():
        person_id = request.args.get('person_id')
        person_data = db.execute("SELECT * FROM person WHERE id = ?", person_id)
        father_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.father_id WHERE parent.person_id = ?", person_id)
        mother_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.mother_id WHERE parent.person_id = ?", person_id)
        child_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.person_id WHERE parent.father_id = ? OR parent.mother_id = ?", person_id, person_id)
        return render_template("details.html", person_data=person_data, father_data=father_data, mother_data=mother_data, child_data=child_data)
