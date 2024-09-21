from flask import Flask, render_template, request, redirect, url_for

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)


all_books = []


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

