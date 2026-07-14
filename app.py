import os
from flask import Flask, render_template
from flask import request, redirect, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
from flask import send_file
from models.user import db, User
from models.task import Task

import pandas as pd
import matplotlib.pyplot as plt

from flask import (
    send_file,
    jsonify
)

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required
)

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret123"

app.config["JWT_SECRET_KEY"]="jwt-secret"

jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///app.db'

db.init_app(app)

with app.app_context():
    db.create_all()
UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"].strip()

        print("Entered Email:", email)

        user = User.query.filter_by(
            email=email
        ).first()

        print("User:", user)

        if user:
            print("Stored Hash:", user.password)

            result = check_password_hash(
                user.password,
                password
            )

            print("Password Match:", result)

        if user and check_password_hash(
                user.password,
                password):

            print("LOGIN SUCCESS")

            session["user_id"] = user.id

            return redirect("/dashboard")

        print("LOGIN FAILED")

    return render_template("login.html")
'''@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
                user.password,
                password):

            session["user_id"] = user.id

            return redirect("/dashboard")

    return render_template("login.html")

'''
@app.route("/register",  methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        print(name, email, password)

        hashed = generate_password_hash(
            password
        )

        user = User(
            name=name,
            email=email,
            password=hashed
        )

        db.session.add(user)
        db.session.commit()

        print("User created successfully")

        return redirect("/")

    return render_template(
        "register.html"
    )



@app.route("/add_task", methods=["POST"])
def add_task():

    if "user_id" not in session:
        return redirect("/")

    title = request.form["title"]
    description = request.form["description"]
    priority = request.form["priority"]
    status = request.form["status"]

    task = Task(
        title=title,
        description=description,
        priority=priority,
        status=status,
        user_id=session["user_id"]
    )

    db.session.add(task)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/delete_task/<int:id>")
def delete_task(id):

    task = Task.query.get_or_404(id)

    db.session.delete(task)

    db.session.commit()

    return redirect("/dashboard")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/edit_task/<int:id>",
    methods=["GET","POST"]
)
def edit_task(id):

    task = Task.query.get_or_404(id)
    
    if request.method == "POST":

        task.title = request.form["title"]
        task.description = request.form["description"]
        task.priority = request.form["priority"]
        task.status = request.form["status"]
        task.due_date = request.form["due_date"]
        
        db.session.commit()

        return redirect("/dashboard")

    return render_template(
        "edit_task.html",
        task=task
    )
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    search = request.args.get("search")

    if search:

        tasks = Task.query.filter(
            Task.user_id == session["user_id"],
            Task.title.contains(search)
        ).all()

    else:

        tasks = Task.query.filter_by(
            user_id=session["user_id"]
        ).all()

    total = Task.query.filter_by(
        user_id=session["user_id"]
    ).count()

    pending = Task.query.filter_by(
        user_id=session["user_id"],
        status="Pending"
    ).count()

    completed = Task.query.filter_by(
        user_id=session["user_id"],
        status="Completed"
    ).count()

    in_progress = Task.query.filter_by(
        user_id=session["user_id"],
        status="In Progress"
    ).count()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        total=total,
        pending=pending,
        completed=completed,
        in_progress=in_progress
    )

@app.route(
    "/profile",
    methods=["GET","POST"]
)
def profile():

    if "user_id" not in session:
        return redirect("/")

    user = User.query.get(
        session["user_id"] )
    if user is None:
        session.clear()
        return redirect("/")


    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]
        user.bio = request.form["bio"]

        photo = request.files.get("photo")

        if photo and photo.filename != "":

            filename = secure_filename(
                photo.filename
            )
            photo.save(
                os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
            )

            user.profile_pic = filename

        db.session.commit()

        return redirect("/profile")

    return render_template(
        "profile.html",
        user=user
    )
"""def profile():

    if "user_id" not in session:
        return redirect("/")

    user = User.query.get( session["user_id"] )
    return render_template(
        "profile.html",
        user=user
    )"""

@app.route("/export")
def export():

    if "user_id" not in session:
        return redirect("/")

    tasks = Task.query.filter_by(
        user_id=session["user_id"]
    ).all()

    data=[]

    for t in tasks:

        data.append({

            "Title":t.title,
            "Description":t.description,
            "Priority":t.priority,
            "Status":t.status,
            "Due Date":t.due_date


        })

    df = pd.DataFrame(data)

    file="tasks.xlsx"

    df.to_excel(
        file,
        index=False
    )

    return send_file(
        file,
        as_attachment=True
    )

@app.route("/users")
def users():

    users = User.query.all()

    for u in users:
        print(u.id, u.name, u.email, u.password)

    return "Check Terminal"

@app.route("/delete_photo")
def delete_photo():

    user = User.query.get(
        session["user_id"]
    )

    if user.profile_pic:

        path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            user.profile_pic
        )

        if os.path.exists(path):
            os.remove(path)

        user.profile_pic = None
        db.session.commit()

    return redirect("/profile")

if __name__ == "__main__":
    app.run(debug=True)