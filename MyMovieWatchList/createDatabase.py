import sqlite3

db = sqlite3.connect('instance/movies.db')

cursor = db.cursor()

cursor.execute("""CREATE TABLE movie
(
    id INTEGER PRIMARY KEY,
    title VARCHAR(250) NOT NULL UNIQUE, 
    year YEAR NOT NULL, 
    description VARCHAR(250),
    rating FLOAT NOT NULL,
    ranking INTEGER NOT NULL,
    review VARCHAR(2000) NOT NULL, 
    img_url VARCHAR(250) NOT NULL
)""")

