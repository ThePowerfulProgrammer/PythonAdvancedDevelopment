from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
import requests
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)



# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class User(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    
    # List of blog posts attached to a  user
    posts: Mapped[List['BlogPost']] = relationship(back_populates="author")
    
    # List of comments by a user
    comments: Mapped[List['Comment']] = relationship(back_populates='comment_author')
    
    def __repr__(self):
        return self.name
    
    
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    author_id: Mapped[int] = mapped_column(Integer,ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")
    
    post_comments: Mapped[List['Comment']] = relationship(back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] =  mapped_column(String(), nullable=False)
    
    
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    comment_author = relationship("User", back_populates="comments")
    
    blog_id: Mapped[int] = mapped_column(Integer, ForeignKey('blog_posts.id'))
    parent_post = relationship("BlogPost", back_populates="post_comments")
    

with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)        
    return decorated_function
    

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if (user):
            print("User email exists")
            flash("You have already signed up with that email, log in instead.")
            return redirect(url_for("login"))
        
        password = request.form["password"]
        name = request.form["name"]        
        saltedPassword = generate_password_hash(password, 'pbkdf2', 8)
        
        user = User(email=email, password=saltedPassword,name=name)
        login_user(user)
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))        
    else:        
        return render_template("register.html", form=form)



@app.route('/login', methods=['GET', "POST"])
def login():
    loginForm = LoginForm()
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if (user):
            if (check_password_hash(user.password, password)):
                login_user(user)
                print(f"{user} logged in")
                return redirect(url_for('get_all_posts'))
            else:
                flash("Password is not correct, please try again")
                return redirect(url_for("login"))
        elif ( not user):
            flash("That email does not exist, please try again")
            return redirect(url_for("login"))        
        
    return render_template("login.html", form=loginForm)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data,
            comment_author = current_user,
            parent_post=requested_post
            )
        db.session.add(comment)
        db.session.commit()

    return render_template("post.html", post=requested_post,current_user=current_user, form=form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)




@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)



@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
