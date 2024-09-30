from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import requests


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
db.init_app(app)
Bootstrap5(app)


class Movie(db.Model):
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str]  = mapped_column(String(2000), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    
    
    def __repr__(self) -> str:
        
        return f"<Movie {self.title}>"


class MyForm(FlaskForm):
    
    name = StringField(label="Movie name", validators=[DataRequired(), Length(min=1)])

# DB created
# with app.app_context():
#     db.create_all()

with app.app_context():
    
    pass




@app.route("/")
def home():
    # Grab all movies
    all_movies = db.session.execute(db.select(Movie).order_by(Movie.id)).scalars()
    
    return render_template(template_name_or_list="index.html", all_movies=all_movies)

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def update(id):    
    if request.method == "POST":
        movieRating = request.form['rating']
        movieReview = request.form['review']
        movie = db.get_or_404(Movie, id)
        
        movie.rating = movieRating
        movie.review = movieReview
        
        db.session.commit()
        
        return redirect(url_for('home'))
    else:
        return render_template(template_name_or_list='edit.html', id=id)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    id = request.args.get('id')
    
    movie = db.get_or_404(Movie, id)
    db.session.delete(movie)
    db.session.commit()
    
    return redirect(url_for('home'))

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = MyForm()
    
    if request.method == "GET":
       return render_template(template_name_or_list='add.html', form=form)
    



if __name__ == '__main__':
    app.run(debug=True)
