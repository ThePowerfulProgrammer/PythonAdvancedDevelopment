from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'I&HNKY91Y:0Mhksh3pArK{'




# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Create login manager
login_manager = LoginManager()
login_manager.init_app(app)

# CREATE TABLE IN DB


class User(UserMixin,db.Model) :
    

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    
    def __repr__(self):
        return self.name



with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

     


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        saltedPassword = generate_password_hash(password, 'pbkdf2', 8)
        
        user = User(name=name,email=email,password=saltedPassword)
        login_user(user)
        if (current_user.is_authenticated):
            print("Logged in")
        else:
            print("Fail")
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("secrets",name=name))
    else:
        return render_template("register.html")

@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)

@app.route('/login', methods=['GET','POST'])
def login():
    if (request.method == "POST"):

        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if (user):
            if (check_password_hash(user.password, password)):
                login_user(user)
                print(f"{user} logged in ")
                return redirect(url_for("home"))
        else:
            print("Imposter")
            return redirect(url_for("login"))
        
    return render_template("login.html")





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download', methods=["GET"])
@login_required
def download():
    return send_from_directory('static', path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
