from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import requests
from secret import bearerTokenOne, bearerTokenTwo
from sqlalchemy import desc



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
        
        return f"{self.title}"
    
    def getId(self) -> int:
        return self.id


class MyForm(FlaskForm):
    
    name = StringField(label="Movie name", validators=[DataRequired(), Length(min=1)])

# DB created
# with app.app_context():
#     db.create_all()

with app.app_context():
    
    pass




@app.route("/")
def home():
    movies = db.session.execute(db.select(Movie).order_by(desc(Movie.rating))).scalars()
    moviesRatingDict = {
        
    }
    primaryKeys = []
    
    for movie in movies:
        
        movieDbObj = db.get_or_404(Movie, movie.id)
        primaryKeys.append(movie.id)
        
        if movieDbObj.title not in moviesRatingDict:
            moviesRatingDict[movieDbObj.title] = movieDbObj.rating
            
    rankingsAvailable = [i+1 for i in range(10)]
    moviesRanking = {}
    
    for k,v in moviesRatingDict.items():
        if k not in moviesRanking:
            moviesRanking[k] = rankingsAvailable[-1]
            rankingsAvailable.pop()
            
        

    count = 0
    # Now assign rankings to movie
    for k,v in moviesRanking.items():
        
        movieObj = db.get_or_404(Movie, primaryKeys[count])
        
        movieObj.ranking = v
        db.session.commit()
        
        count += 1
    
    
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
    if request.method == "POST":
        title = request.form['name']
        endpoint = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {bearerTokenOne}"
        }
        data = {
            'query': title,
            "include_adult": False,
        }
        response = requests.get(endpoint,  headers=headers, params=data)
        JSON  = response.json()
        try:

            
            numberOfMatches = len(JSON['results'])
            
            allMovieTitles = [JSON['results'][i]['original_title'] for i in range(numberOfMatches)]
            allMovieReleaseDates = [JSON['results'][i]['release_date'] for i in range(numberOfMatches)]
            allMovieIds = [JSON['results'][i]['id'] for i in range(numberOfMatches)]

            # for i in range(numberOfMatches):
            #     print(JSON['results'][i]['original_title']) 
            #     print(JSON['results'][i]['release_date'])
            #     print(JSON['results'][i]['overview'])                
            
            originalTitle = JSON['results'][0]['original_title']
            year = JSON['results'][0]['release_date']
            description = JSON['results'][0]['overview']
            rating = JSON['results'][0]['vote_average']
            ranking = ""
            review = ""
            img_url = f'https://image.tmdb.org/t/p/w500{JSON["results"][0]["poster_path"]}'
            
            titlesAndDateAndIds = list(zip(allMovieTitles,allMovieReleaseDates,allMovieIds))
            return render_template(template_name_or_list='select.html', titlesAndDate=titlesAndDateAndIds )            
        except IndexError:
            print("JSON DNE")
        
        form.name.data = ""
        return render_template(template_name_or_list='add.html', form=form)

    
    if request.method == "GET":
       return render_template(template_name_or_list='add.html', form=form)
    
@app.route("/confirm")
def confirmAdd():
    id = request.args.get('id')
    
    detailsEndpoint = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearerTokenTwo}"
    }

    
    data = requests.get(url=detailsEndpoint, headers=headers)

    try:
            
        # I already have id
        title = data.json()['original_title']
        year = data.json()['release_date']
        description = data.json()['overview']
        rating = data.json()['vote_average']
        ranking = 0
        review = ""
        img_url = f"https://image.tmdb.org/t/p/w500/{data.json()['poster_path']}"
        
        movie = Movie(title=title,year=year,description=description,rating=rating,
                    ranking=ranking,review=review, img_url=img_url)
        db.session.add(movie)
        db.session.commit()
        
        
        
        movieId = db.session.execute(
            db.select(Movie).where(Movie.title == title)
        ).scalar()
        
        id = movieId.id
        return render_template(template_name_or_list='edit.html', id=id)
    except:
        return redirect(url_for('home'))
    
    
    
    


if __name__ == '__main__':
    app.run(debug=True)
