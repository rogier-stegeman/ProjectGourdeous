from flask import Flask, render_template, url_for, request, redirect, flash
from Bio import Entrez
import mysql.connector
from Bio import Medline

app = Flask(__name__)
#app = Flask(__name__)
#wsgi_app = app.wsgi_app
#print(open("templates/home.html","r").read())


@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/textmine')
def textmine():
    organisms = ['bitter gourd', 'yam', 'Momordica charantia', 'Dioscorea batatas']
    compounds = ['fatty acid', 'insulin', 'cholesterol', 'sugar', 'glucose', 'vitamin A', 'vitamin B', 'vitamin C',
                 'vitamin E', 'calcium', 'iron', 'potassium']
    health_effects = ['diabetes', 'cancer', 'weigth loss', 'cough', 'wounds', 'rheumatism', 'laxative', 'diarrhea',
                      'abdominal pain', 'fever', 'hypoglycemia', 'urinary incontinence', 'chest pain', 'miscarriage']
    return render_template('textmine.html', organisms=organisms, compounds=compounds, health_effects=health_effects)

@app.route('/busy', methods=['GET','POST'])
def submitter():
    #return render_template("sorry.html")
    #return render_template("Busy.html")
    #This function is meant to allow the user to add data in the form of search requests to the database
    # in order to expand the database.
    organisme = request.form['search1']
    zoekwoord = request.form['search2']
    email = request.form['search3']
    zoekwoord = "diarrhea"
    organisme = "dioscorea batatas"
    conn = mysql.connector.connect(user='owe8_pg9', password='blaat1234',
                                    host="localhost",
                                    database='owe8_pg9')
    conn.close() #code voor textmining invoegen of verander render template in sorry.html.
    return render_template("Busy.html")


@app.route('/sunburst')
def sunburst():
    return render_template("sunburst.html")


@app.route('/help')
def helppage():
    return render_template("help.html")


@app.route('/cook')
def cook():
    return render_template("cook.html")


if __name__ == '__main__':
    app.run(debug=True)