from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_sqlalchemy import SQLAlchemy

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqllite:///books-collection.db"
db.init_app(app)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Book {self.title} >"

with app.app_context():
    pass

@app.route('/')
def home():
    all_books = db.session.execute(db.select(Book).order_by(Book.id)).scalars()
    return render_template(template_name_or_list="index.html", all_books=all_books)

# Add a dictionary object to all_books
@app.route("/add", methods=['GET', 'POST'])
def add():
    pass
    
if __name__ == "__main__":
    app.run(debug=True)

