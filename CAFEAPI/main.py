from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy import func
import random


'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    
    def __repr__(self):
        return f"<Cafe {self.name}>"


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")




# HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def getRecord():
    if request.method == "GET":
        # i need to grab a random db object
        rows = db.session.execute(db.select(func.count()).select_from(Cafe)).scalar()
        print(rows)
        
        randomRow = random.randint(1,rows)
        print(randomRow)
        
        cafe = db.get_or_404(Cafe, randomRow)
        print(cafe)
        data = {"name":cafe.name,
                "map_url":cafe.map_url,
                "img_url":cafe.img_url, 
                "location":cafe.location,
                "seats":cafe.seats, 
                "has_toilet":cafe.has_toilet,
                "has_wifi":cafe.has_wifi,
                "has_sockets":cafe.has_sockets,
                "can_take_calls":cafe.can_take_calls,
                "coffee_price":cafe.coffee_price}

        json = jsonify(Cafe=data)
        
        return json
    else:
        
        return "<h1>Hello world</h1>"



# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
