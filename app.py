import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_login import LoginManager, login_required
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # return User.get(user_id)
    return None


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLite database
con = sqlite3.connect("familytree.db", check_same_thread=False)
con.row_factory = sqlite3.Row
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmation = request.form['confirmation']
        check_username = db.execute("SELECT username FROM users WHERE username = ?", [username])
        if not check_username.fetchone() is None:
            return render_template("login.html", error="Unique name is required!")
        if not username:
            return render_template("login.html", error="Name is required!")
        elif not password:
            return render_template("login.html", error="Password is required!")
        elif not confirmation:
            return render_template("login.html", error="Password confirmation is required!")
        elif not password == confirmation:
            return render_template("login.html", error="Password should be equal to Password confirmation!")
        else:
            password_hash = generate_password_hash(password)
            sql = "INSERT INTO users (username, hash) VALUES ('{username}', '{password_hash}');"
            db.executescript(sql)
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
        username = request.form.get("username")

        # Query database for username
        db.execute("SELECT id, username, hash FROM users WHERE username = ?", [username])
        rows = db.fetchall()
        for row in rows:
            u_id = row[0]
            u_user = row[1]
            u_hash = row[2]

        # Ensure username exists and password is correct
        if u_hash is None or not check_password_hash(u_hash, request.form.get("password")):
            return render_template("login.html", error="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = u_id

        # Redirect user to home page
        return redirect("/tree")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    con.close()
    session.clear()
    return redirect("/")


@app.route("/tree", methods=["GET", "POST"])
# @login_required
def tree():
    if request.method == 'POST':
        search = request.form['search']
        if search == "":
            user_data = db.execute("SELECT * FROM person").fetchall()
        if search != "":
            user_data = db.execute("SELECT * FROM person WHERE lastname LIKE ? OR name LIKE ?", [search, search]).fetchall()
        return render_template("tree.html", user_data=user_data, search=search)
    else:
        user_data = db.execute("SELECT * FROM person").fetchall()
        return render_template("tree.html", user_data=user_data)


@app.route("/add", methods=["GET", "POST"])
# @login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        birth_date = request.form['birth_date']
        birth_place = request.form['birth_place']
        death_date = request.form['death_date']
        death_place = request.form['death_place']
        sex = request.form['sex']
        try:
            father_id = request.form['father_id']
        except:
            father_id = ""
        try:
            mother_id = request.form['mother_id']
        except:
            mother_id = ""
        sql = f"INSERT INTO person (name, lastname, birth_date, birth_place, death_date, death_place, sex) VALUES ('{name}', '{lastname}', '{birth_date}', '{birth_place}', '{death_date}', '{death_place}', '{sex}');"
        db.executescript(sql)
        person = db.execute("SELECT id FROM person WHERE name = ? AND lastname = ? AND birth_date = ? AND birth_place = ? AND death_date = ? AND death_place = ? AND sex = ? ORDER BY id DESC", [name, lastname, birth_date, birth_place, death_date, death_place, sex])
        person_id = person.fetchone()
        sql = f"INSERT INTO parent (person_id, father_id, mother_id) VALUES ('{person_id}', '{father_id}', '{mother_id}');"
        db.executescript(sql)
        return redirect("/tree")
    else:
        man = db.execute("SELECT * FROM person WHERE sex = ?", ['male']).fetchall()
        woman = db.execute("SELECT * FROM person WHERE sex = ?", ['female']).fetchall()
        return render_template("add.html", man=man, woman=woman)


@app.route("/edit", methods=["GET", "POST"])
# @login_required
def edit():
    if request.method == 'POST':
        person_id = request.form['person_id']
        name = request.form['name']
        # middlename = request.form['middlename']
        lastname = request.form['lastname']
        birth_date = request.form['birth_date']
        birth_place = request.form['birth_place']
        death_date = request.form['death_date']
        death_place = request.form['death_place']
        sex = request.form['sex']
        try:
            father_id = request.form['father_id']
        except:
            father_id = ""
        try:
            mother_id = request.form['mother_id']
        except:
            mother_id = ""
        print(f"'{person_id}', '{father_id}', '{mother_id}'")
        sql = f"SELECT * FROM parent WHERE person_id = {person_id};"
        inparents = db.execute(sql).fetchone()
        if not inparents == None:
            sql = f"UPDATE person SET name = '{name}', lastname = '{lastname}', birth_date = '{birth_date}', birth_place = '{birth_place}', death_date = '{death_date}', death_place = '{death_place}', sex = '{sex}' WHERE id = {person_id}; UPDATE parent SET father_id = '{father_id}', mother_id = '{mother_id}' WHERE person_id = '{person_id}';"
        else:
            sql = f"UPDATE person SET name = '{name}', lastname = '{lastname}', birth_date = '{birth_date}', birth_place = '{birth_place}', death_date = '{death_date}', death_place = '{death_place}', sex = '{sex}' WHERE id = {person_id}; INSERT INTO parent (person_id, father_id, mother_id) VALUES ('{person_id}', '{father_id}', '{mother_id}');"
        db.executescript(sql)
        return redirect(f"/details?person_id={person_id}")
    else:
        person_id = request.args.get('person_id')
        person_data = db.execute("SELECT * FROM person WHERE id = ?", [person_id]).fetchone()
        father = db.execute("SELECT * FROM parent JOIN person ON parent.father_id = person.id WHERE parent.person_id = ?", [person_id]).fetchone()
        man = db.execute(f"SELECT * FROM person WHERE person.sex = ? and person.birth_date < ? ORDER BY ?", ['male', '{person_data[birth_date]}', 'birth_date']).fetchall()
        mother = db.execute("SELECT * FROM parent JOIN person ON parent.mother_id = person.id WHERE parent.person_id = ?", [person_id]).fetchone()
        woman = db.execute(f"SELECT * FROM person WHERE person.sex = ? and person.birth_date < ? ORDER BY ?", ['female', '{person_data[birth_date]}', 'birth_date']).fetchall()
        return render_template("edit.html", person_data=person_data, father=father, mother=mother, man=man, woman=woman, person_id=person_id)


@app.route("/details")
# @login_required
def details():
    person_id = request.args.get('person_id')
    if not len(person_id) == 0 or not person_id == None:
        person_data = db.execute("SELECT * FROM person WHERE id = ?", [person_id]).fetchall()
        father_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.father_id WHERE parent.person_id = ?", [person_id]).fetchall()
        mother_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.mother_id WHERE parent.person_id = ?", [person_id]).fetchall()
        child_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.person_id WHERE parent.father_id = ? OR parent.mother_id = ?", [person_id, person_id]).fetchall()
        return render_template("details.html", person_data=person_data, father_data=father_data, mother_data=mother_data, child_data=child_data)
    else:
        return redirect("/tree")


@app.route("/add_parent", methods=["GET", "POST"])
#@login_required
def add_parent():
    if request.method == 'POST':
        origin_person_id = request.form['person_id']
        name = request.form['name']
        lastname = request.form['lastname']
        birth_date = request.form['birth_date']
        birth_place = request.form['birth_place']
        death_date = request.form['death_date']
        death_place = request.form['death_place']
        sex = request.form['sex']
        try:
            father_id = request.form['father_id']
        except:
            father_id = ""
        try:
            mother_id = request.form['mother_id']
        except:
            mother_id = ""
        sql = f"INSERT INTO person (name, lastname, birth_date, birth_place, death_date, death_place, sex) VALUES ('{name}', '{lastname}', '{birth_date}', '{birth_place}', '{death_date}', '{death_place}', '{sex}');"
        db.executescript(sql)
        person = db.execute("SELECT id FROM person WHERE name = ? AND lastname = ? AND birth_date = ? AND birth_place = ? AND death_date = ? AND death_place = ? AND sex = ? ORDER BY id DESC", [name, lastname, birth_date, birth_place, death_date, death_place, sex])
        person_id = person.fetchone()
        sql = f"INSERT INTO parent (person_id, father_id, mother_id) VALUES ('{person_id}', '{father_id}', '{mother_id}');"
        db.executescript(sql)
        print("add_parent")
        if sex == "male":
            sql = f"INSERT INTO parent (person_id, father_id) VALUES ('{origin_person_id}', '{person_id}');"
        if sex == "female":
            sql = f"INSERT INTO parent (person_id, mother_id) VALUES ('{origin_person_id}', '{person_id}');"
        db.executescript(sql)
        return redirect(f"/details?person_id={origin_person_id}")
    else:
        man = db.execute("SELECT * FROM person WHERE sex = ?", ['male']).fetchall()
        woman = db.execute("SELECT * FROM person WHERE sex = ?", ['female']).fetchall()
        return render_template("add.html", man=man, woman=woman)
