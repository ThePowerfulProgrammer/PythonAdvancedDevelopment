from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy import func, exists
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
    
@app.route("/all", methods=['GET'])
def getAllRecords():
    if request.method == "GET":
        
        rows = db.session.execute(db.select(Cafe)).scalars()
        dict = {"cafe": []}
        
        for row in rows:
            data = {"name":row.name,
                    "map_url":row.map_url,
                    "img_url":row.img_url, 
                    "location":row.location,
                    "seats":row.seats, 
                    "has_toilet":row.has_toilet,
                    "has_wifi":row.has_wifi,
                    "has_sockets":row.has_sockets,
                    "can_take_calls":row.can_take_calls,
                    "coffee_price":row.coffee_price}
            
            dict['cafe'].append(data)
                
        return jsonify(dict)

@app.route("/search", methods=['GET'])
def searchRecord():
        query_params = request.args
        
        location = query_params.get('name')
        search = f"%{location}%"
        print(search)
        cafes = Cafe.query.filter(Cafe.location.like(search)).all()
        print(cafes)
            
        if cafes:
                
            dict = {"cafe":[]}
            for cafe in cafes:
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
                dict['cafe'].append(data)

            return jsonify(dict)
        
        else:
            return jsonify(error={"Not found": "Sorry we do not have a cafe at that location"})

# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def addCafe():
    if request.method == "POST":
        cafe = Cafe(
            name=request.args.get("name"),
            map_url=request.args.get("map_url"),
            img_url=request.args.get("img_url"),
            location=request.args.get("location"),
            has_sockets=True if request.args.get("sockets") == "Yes" else False,
            has_toilet=True if request.args.get("toilet") == "Yes" else False,
            has_wifi=True if request.args.get("wifi") == "Yes" else False,
            can_take_calls=True if request.args.get("calls") == "Yes" else False,
            seats=request.args.get("seats"),
            coffee_price=request.args.get("coffee_price"),
        )
        db.session.add(cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe"})
    




# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["GET", "POST", "PATCH"])
def updateCoffeePrice(cafe_id):

    exists = db.session.query(db.exists().where(Cafe.id == cafe_id)).scalar()
    
    if exists:
            

        print(cafe_id)
        cafe = db.get_or_404(Cafe,cafe_id)
        new_price = request.args.get("new_price")
        
        print(cafe)
        print(new_price)
        print(cafe.id)
        print(cafe.coffee_price)
        
        cafe.coffee_price = new_price
        db.session.commit()

        return redirect(url_for("home"))
    else:
        return jsonify(error={"Unsuccessful": "Cafe does not exist"})


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def deleteCafe(cafe_id):

    API_KEY = "APIKEY"
    key = request.args.get("api-key")

    if key != API_KEY:
        return jsonify(error={"Status Code": "401 error"})
    else:
        cafe = db.get_or_404(Cafe, cafe_id)
        rows = db.session.execute(db.select(func.count()).select_from(Cafe)).scalar()
        
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(success={"Status Code": "200 Cafe Deleted"})
    
    


if __name__ == '__main__':
    app.run(debug=True)
