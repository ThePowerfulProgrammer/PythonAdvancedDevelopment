from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, TimeField, RadioField, SelectField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap4
import csv

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
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap4(app)



class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location_url = URLField(label='Website url', validators=[DataRequired()])
    open_time = TimeField(label='Open time', validators=[DataRequired()])
    close_time = TimeField(label='Closing Time', validators=[DataRequired()])
    coffee_rating = SelectField(label='Brew Intensity', choices=['☕️','☕️☕️','☕️☕️☕️','☕️☕️☕️☕️','☕️☕️☕️☕️☕️'] , validators=[DataRequired()])
    wifi_rating = SelectField(label='Wifi Strength?', choices=['✘','💪','💪💪','💪💪💪','💪💪💪💪','💪💪💪💪💪'], validators=[DataRequired()])
    power_outlets = SelectField(label='Power Outlets?', choices=['✘','🔌','🔌🔌','🔌🔌🔌','🔌🔌🔌🔌','🔌🔌🔌🔌🔌'], validators=[DataRequired()])
    submit = SubmitField('Submit')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if (request.method == "GET"):
        return render_template(template_name_or_list='add.html', form=form)
    elif (request.method == 'POST'):
        if (form.validate_on_submit()):
            print("Submitted")

            # open csv and write data
            data = [form.cafe.data,
            form.location_url.data,
            form.open_time.data,
            form.close_time.data,
            form.coffee_rating.data,
            form.wifi_rating.data,
            form.power_outlets.data]
            with open('findAModernCafe/cafe-data.csv', mode='a', encoding='utf-8', newline='\n') as writeFile:
                csvWriter = csv.writer(writeFile)
                csvWriter.writerow(data)
                
            form = CafeForm(formdata=None)
            return render_template(template_name_or_list='add.html', form=form)
            
        


@app.route('/cafes')
def cafes():
    with open('findAModernCafe/cafe-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True)
