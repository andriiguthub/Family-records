import os
import sqlite3
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, \
    current_user
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# init SQLAlchemy so we can use it later in our models
app.config['SECRET_KEY'] = '9E3M3wqAM7yIFIEI00BYA2xyKxVDoy6wNMPc9L4e'
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'familytree.db')
udb = SQLAlchemy(app)

class users(UserMixin, udb.Model):
    id = udb.Column(udb.Integer, primary_key=True)
    username = udb.Column(udb.String(80), unique=True, nullable=False)
    hash = udb.Column(udb.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


# Configure login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

#Configure to use SQLite database
con = sqlite3.connect("familytree.db", check_same_thread=False)
con.row_factory = sqlite3.Row
db = con.cursor()


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/tree")
    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        apikey = generate_password_hash(os.environ['APIKEY'])
        if not apikey:
            return render_template("register.html", error="APIKEY IS NOT SET!")
        username = request.form['username']
        password = request.form['password']
        confirmation = request.form['confirmation']
        code = request.form['code']
        user = users.query.filter_by(username=username).first()
        if user:
            return render_template("register.html", error="Unique name is required!")
        if not username:
            return render_template("register.html", error="Name is required!")
        elif not password:
            return render_template("register.html", error="Password is required!")
        elif not confirmation:
            return render_template("register.html", error="Password confirmation is required!")
        elif not password == confirmation:
            return render_template("register.html", \
                                   error="Password should be equal to Password confirmation!")
        if not check_password_hash(apikey, code):
            return render_template("register.html", \
                                   error="Incorrect 2FA code, check your messages and try again!")

        else:
            new_user = users(username=username, hash=generate_password_hash(password))
            udb.session.add(new_user)
            udb.session.commit()
            return render_template("login.html",  error="Registration successfull!")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", error="Name is required!")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="Password is required!")
        username = request.form.get("username")
        password = request.form.get('password')
        user = users.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.hash, password):
            return render_template("login.html", error="invalid username and/or password")
        # Redirect user to home page
        login_user(user)
        return redirect("/tree")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        user = db.execute("SELECT * FROM users").fetchall()
        if not user:
            return render_template("register.html", error="Create user!")
        return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/tree", methods=["GET", "POST"])
@login_required
def tree():
    if request.method == 'POST':
        search = request.form['search']
        if search == "":
            sql = "SELECT * FROM person ORDER BY lastname"
            user_data = db.execute(sql).fetchall()
        if search != "":
            user_data = db.execute("SELECT * FROM person WHERE lastname LIKE ? OR name LIKE ?", \
                                   [search, search]).fetchall()
        return render_template("tree.html", user_data=user_data, search=search)
    else:
        user_data = db.execute("SELECT * FROM person").fetchall()
        return render_template("tree.html", user_data=user_data)


@app.route("/add", methods=["GET", "POST"])
@login_required
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
        sql = f"INSERT INTO person (name, lastname, birth_date, birth_place, death_date, \
            death_place, sex) VALUES ('{name}', '{lastname}', '{birth_date}', '{birth_place}', \
                '{death_date}', '{death_place}', '{sex}');"
        db.executescript(sql)
        person = db.execute("SELECT id FROM person WHERE name = ? AND lastname = ? AND \
                            birth_date = ? AND birth_place = ? AND death_date = ? AND \
                            death_place = ? AND sex = ? ORDER BY id DESC", \
                                [name, lastname, birth_date, birth_place, death_date, \
                                 death_place, sex])
        person_id = person.fetchone()['id']
        sql = f"INSERT INTO parent (person_id, father_id, mother_id) VALUES \
            ('{person_id}', '{father_id}', '{mother_id}');"
        db.executescript(sql)
        return redirect("/tree")
    else:
        man = db.execute("SELECT * FROM person WHERE sex = ?", ['male']).fetchall()
        woman = db.execute("SELECT * FROM person WHERE sex = ?", ['female']).fetchall()
        return render_template("add.html", man=man, woman=woman, action="add")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == 'POST':
        person_id = request.form['person_id']
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
        print(f"'{person_id}', '{father_id}', '{mother_id}'")
        sql = f"SELECT * FROM parent WHERE person_id = {person_id};"
        inparents = db.execute(sql).fetchone()
        if not inparents is None:
            sql = f"UPDATE person SET name = '{name}', lastname = '{lastname}', \
                birth_date = '{birth_date}', birth_place = '{birth_place}', \
                    death_date = '{death_date}', death_place = '{death_place}', sex = '{sex}' \
                        WHERE id = {person_id}; UPDATE parent SET father_id = '{father_id}', \
                            mother_id = '{mother_id}' WHERE person_id = '{person_id}';"
        else:
            sql = f"UPDATE person SET name = '{name}', lastname = '{lastname}', \
                birth_date = '{birth_date}', birth_place = '{birth_place}', \
                    death_date = '{death_date}', death_place = '{death_place}', sex = '{sex}' \
                        WHERE id = {person_id}; INSERT INTO parent (person_id, father_id, \
                            mother_id) VALUES ('{person_id}', '{father_id}', '{mother_id}');"
        db.executescript(sql)
        return redirect(f"/details?person_id={person_id}")
    else:
        person_id = request.args.get('person_id')
        person_data = db.execute("SELECT * FROM person WHERE id = ?", [person_id]).fetchone()
        father = db.execute("SELECT * FROM parent JOIN person ON parent.father_id = person.id \
                            WHERE parent.person_id = ?", [person_id]).fetchone()
        man = db.execute(f"SELECT * FROM person WHERE person.sex = ? AND person.birth_date < ? \
                        AND id != {person_id} ORDER BY ?", ['male', '{person_data[birth_date]}', \
                        'birth_date']).fetchall()
        mother = db.execute("SELECT * FROM parent JOIN person ON parent.mother_id = person.id \
                            WHERE parent.person_id = ?", [person_id]).fetchone()
        woman = db.execute(f"SELECT * FROM person WHERE person.sex = ? AND person.birth_date < ? \
                            AND person.id != {person_id} ORDER BY ?", ['female', \
                            '{person_data[birth_date]}', 'birth_date']).fetchall()
        return render_template("edit.html", person_data=person_data, father=father, \
                               mother=mother, man=man, woman=woman, person_id=person_id)


@app.route("/details")
@login_required
def details():
    person_id = request.args.get('person_id')
    if not len(person_id) == 0 or not person_id is None:
        person_data = db.execute("SELECT * FROM person WHERE id = ?", [person_id]).fetchone()
        spouse_data = db.execute("SELECT * FROM person WHERE person.id IN (SELECT spouse.spouse_id from spouse WHERE person_id = ?);", [person_id]).fetchall()
        father_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.father_id WHERE parent.person_id = ?", [person_id]).fetchone()
        mother_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.mother_id WHERE parent.person_id = ?", [person_id]).fetchone()
        child_data = db.execute("SELECT * FROM person JOIN parent ON person.id = parent.person_id WHERE \
            parent.father_id = ? OR parent.mother_id = ?", [person_id, person_id]).fetchall()
        return render_template("details.html", person_data=person_data, spouse_data=spouse_data, father_data=father_data, mother_data=mother_data, child_data=child_data)
    else:
        return redirect("/tree")


@app.route("/add_parent", methods=["GET", "POST"])
@login_required
def add_parent():
    if request.method == 'POST':
        try:
            origin_person_id = request.form['origin_person_id']
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
            sql = f"INSERT INTO person (name, lastname, birth_date, birth_place, death_date, death_place, sex) VALUES \
                ('{name}', '{lastname}', '{birth_date}', '{birth_place}', '{death_date}', '{death_place}', '{sex}');"
            db.executescript(sql)
            person = db.execute("SELECT id FROM person WHERE name = ? AND lastname = ? AND birth_date = ? AND \
                birth_place = ? AND death_date = ? AND death_place = ? AND sex = ? ORDER BY id DESC", \
                                [name, lastname, birth_date, birth_place, death_date, death_place, sex])
            person_id = person.fetchone()['id']
            print(person_id)
            sql = f"INSERT INTO parent (person_id, father_id, mother_id) VALUES ('{person_id}', '{father_id}', '{mother_id}');"
            db.executescript(sql)
            try:
                if sex == "male":
                    sql = f"UPDATE parent SET father_id = '{person_id}' WHERE person_id = {origin_person_id};"
                if sex == "female":
                    sql = f"UPDATE parent SET mother_id = '{person_id}' WHERE person_id = {origin_person_id};"
                db.executescript(sql)
            except Exception as error:
                print("SQL ERROR!!!", error)
            return redirect(f"/details?person_id={origin_person_id}")
        except Exception as error:
            print("TRY ERRROR!!!", error)
    else:
        origin_person_id = request.args.get('person_id')
        man = db.execute("SELECT * FROM person WHERE sex = ? AND id != ?", ['male', origin_person_id]).fetchall()
        woman = db.execute("SELECT * FROM person WHERE sex = ? AND id != ?", ['female', origin_person_id]).fetchall()
        return render_template("add.html", man=man, woman=woman, origin_person_id=origin_person_id, action=f"add_parent?person_id={origin_person_id}")

@app.route("/add_child", methods=["GET", "POST"])
@login_required
def add_child():
    if request.method == 'POST':
        try:
            origin_person_id = request.form['origin_person_id']
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
            sql = f"INSERT INTO person (name, lastname, birth_date, birth_place, death_date, death_place, sex) VALUES \
                ('{name}', '{lastname}', '{birth_date}', '{birth_place}', '{death_date}', '{death_place}', '{sex}');"
            db.executescript(sql)
            person = db.execute("SELECT id FROM person WHERE name = ? AND lastname = ? AND birth_date = ? AND \
                birth_place = ? AND death_date = ? AND death_place = ? AND sex = ? ORDER BY id DESC", \
                                [name, lastname, birth_date, birth_place, death_date, death_place, sex])
            person_id = person.fetchone()['id']
            sql = f"SELECT sex FROM person where id = '{origin_person_id}';"
            parent_sex = db.execute(sql).fetchone()['sex']
            if parent_sex == "male":
                sql = f"INSERT INTO parent (person_id, father_id, mother_id) VALUES ('{person_id}', '{origin_person_id}', '{mother_id}');"
            if parent_sex == "female":
                sql = f"INSERT INTO parent (person_id, father_id, mother_id) VALUES ('{person_id}', '{father_id}', '{origin_person_id}');"
            try:
                db.executescript(sql)
            except Exception as error:
                print("SQL ERROR!!!", error)
            return redirect(f"/details?person_id={origin_person_id}")
        except Exception as error:
            print("TRY ERRROR!!!", error)
    else:
        origin_person_id = request.args.get('person_id')
        origin_person_sex = db.execute("SELECT sex FROM person WHERE id = ?", [origin_person_id]).fetchone()['sex']
        if origin_person_sex == 'male':
            father = db.execute("SELECT * FROM person WHERE id = ?", [origin_person_id]).fetchone()
        else: father = ""
        if origin_person_sex == 'female':
            mother = db.execute("SELECT * FROM person WHERE id = ?", [origin_person_id]).fetchone()
        else: mother = ""
        man = db.execute("SELECT * FROM person WHERE sex = ?", ['male']).fetchall()
        woman = db.execute("SELECT * FROM person WHERE sex = ?", ['female']).fetchall()
        return render_template("add.html", father=father, mother=mother, man=man, woman=woman, \
                               origin_person_id=origin_person_id, action=f"add_child?person_id={origin_person_id}")

@app.route("/add_spouse", methods=["GET", "POST"])
@login_required
def add_spouse():
    if request.method == 'POST':
        try:
            origin_person_id = request.form['origin_person_id']
            spouse = request.form['spouse']
            marriage_date = request.form['marriage_date']
            divorce_date = request.form['divorce_date']
            sql = f"INSERT INTO spouse (person_id, spouse_id, marriage_date, divorce_date) VALUES ('{origin_person_id}', '{spouse}', '{marriage_date}', '{divorce_date}');"
            db.executescript(sql)
            sql = f"INSERT INTO spouse (person_id, spouse_id, marriage_date, divorce_date) VALUES ('{spouse}', '{origin_person_id}', '{marriage_date}', '{divorce_date}');"
            db.executescript(sql)
            return redirect(f"/details?person_id={origin_person_id}")
        except Exception as error:
            print("ERRROR!!!", error)
            return redirect(f"/details?person_id={origin_person_id}")
    else:
        origin_person_id = request.args.get('person_id')
        people = db.execute("SELECT * FROM person WHERE id !=?",[origin_person_id]).fetchall()
        return render_template("add_spouse.html", people=people, origin_person_id=origin_person_id, action=f"add_spouse?person_id={origin_person_id}")
