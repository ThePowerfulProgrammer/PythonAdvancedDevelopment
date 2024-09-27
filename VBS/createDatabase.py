import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_sqlalchemy import SQLAlchemy



class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"
db.init_app(app)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Book {self.title}> "
  
# Creation Done  
# with app.app_context():
#     db.create_all()

with app.app_context():
    # Create
    # book = Book(title="Berserk Volume 26", author="Kentaro Miura", rating=7)
    # db.session.add(book)
    # db.session.commit()
    
    # Read
    # books = db.session.execute(db.select(Book).order_by(Book.title)).scalars()
    # for book in books:
    #     print(book)   
        
    # Read
    # book = db.get_or_404(Book,1)
    # print(book)
    
    #Update -> Read -> then modify
    
    # delete
    # db.session.delete(book)
    # db.session.commit()
    pass
    
@app.route("/")
def home():
    # book = Book(title="Berserk Volume 26", author="Kentaro Miura", rating=7)
    # db.session.add(book)
    # db.session.commit()
    all_books = db.session.execute(db.select(Book).order_by(Book.id)).scalars()
    return render_template(template_name_or_list="index.html", all_books=all_books)

@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        book = Book(
            title=request.form['bName'],
            author=request.form['bAuthor'],
            rating=request.form['rating']
        )

        db.session.add(book)
        db.session.commit()
        
        return render_template(template_name_or_list='add.html')
    
    return render_template(template_name_or_list='add.html')
    
@app.route("/edit/<int:pk>", methods=['GET', 'POST'])
def edit(pk):
    book = db.get_or_404(Book,ident=pk)
    if request.method == "POST":
        book_id = request.form['id']
        book = db.get_or_404(Book, book_id)
        book.rating = request.form['rating']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template(template_name_or_list='edit.html', pk=pk, book=book)

@app.route("/delete", methods=['GET', 'POST'])
def delete():
    book_id = request.args.get('id')
    print(book_id)
    book = db.get_or_404(Book, book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('home'))



if __name__ == "__main__":
    
    app.run(debug=True)
    

    
    
    
    