from flask import Flask, render_template, url_for, request, redirect
from  Gourdeous_textminer import connector,entrez_search,db_vullen
from  Jsonmaker import Connection, Inlezen
from flask import Flask



app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('home')) #deze functie verwijst door naar de home pagina


@app.route('/home')
def home():
    return render_template('home.html') # deze functie verwijst naar de home pagina


@app.route('/textmine')
def textmine():
    return render_template('textmine.html') # deze functie verwijst naar de textminer pagina

@app.route('/Done', methods=['GET','POST']) # deze functie verwijst naar de done pagina en haalt informatie op van de textmine pagina
# die gebruikt kan worden door de textmine script en door pubmed
def submitter():
    #This function is meant to allow the user to add data in the form of search requests to the database
    # in order to expand the database.
    organisme = request.form['searchPlant']
    zoekwoord = request.form['searchHealth']
    email = request.form['searchMail']
    data = entrez_search(organisme,zoekwoord,email)
    con = connector()
    db_vullen(data, organisme, zoekwoord, con)
    conn = Connection()
    Inlezen(conn)
    return render_template("Done.html")



@app.route('/sunburst') # deze functie verwijst naar de sunburst pagina
def sunburst():
    return render_template("sunburst.html")


@app.route('/help') # Deze functie verwijst naar de help pagina
def helppage():
    return render_template("help.html")


@app.route('/cook') # deze functie verwijst naar de cooking pagina
def cook():
    return render_template("cook.html")


if __name__ == '__main__':
    app.run(debug=True)