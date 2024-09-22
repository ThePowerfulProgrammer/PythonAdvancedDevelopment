from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
all_books = []


class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Book {self.title}> "

with app.app_context():
    db.create_all()

with app.app_context():
    new_book = Book(id=1, title="Database Design, Implementation and Management", author="Steven Morris, Carlos Coronel, Keeley", rating=4)
    db.session.add(new_book)
    db.session.commit()

@app.route('/')
def home():
    global all_books

    return render_template(template_name_or_list='index.html', all_books=all_books)


# Add a dictionary object to all_books
@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        global all_books
        
        all_books.append( 
                         
            {'title':request.form.get('bName'),
             'author': request.form.get('bAuthor'),
             'rating': int(request.form.get('rating'))
            }

        )
        
        print(all_books)
        return render_template(template_name_or_list='add.html')
    
    return render_template(template_name_or_list='add.html')
    
if __name__ == "__main__":
    app.run(debug=True)

