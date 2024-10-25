from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    
    def __repr__(self):
        return self.name


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        user = User(name=name,email=email,password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("secrets",name=name))
    else:
        return render_template("register.html")

@app.route('/secrets/<string:name>')
def secrets(name):
    
    print("User with the name: ")
    print(name)
    
    return render_template("secrets.html", name=name)

@app.route('/login', methods=['GET','POST'])
def login():
    if (request.method == "POST"):

        email = request.form['email']
        password = request.form['password']
        print(email)
        print(password)
        user = db.session.execute(db.select(User).where((User.email == email) & (User.password == password) )).scalar()
        if (user):
            print(f"{user} logged in ")
            return redirect(url_for("home"))
        else:
            print("Imposter")
            return redirect(url_for("login"))
        
    return render_template("login.html")





@app.route('/logout')
def logout():
    pass


@app.route('/download', methods=["GET"])
def download():
    if (request.method == "GET"):
        return send_from_directory('static', path='files/cheat_sheet.pdf') 


if __name__ == "__main__":
    app.run(debug=True)
