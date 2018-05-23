from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)
#app = Flask(__name__)
wsgi_app = app.wsgi_app
#print(open("templates/home.html","r").read())


@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/sunburst')
def sunburst():
    organisms = ['bitter gourd', 'yam']
    compounds = ['fatty acid', 'insulin', 'cholesterol', 'sugar']
    health_effects = ['diabetic', 'cancer', 'weigth loss']
    return render_template("sunburst.html", organisms=organisms, compounds=compounds, health_effects=health_effects)


@app.route('/help')
def helppage():
    return render_template("help.html")


if __name__ == '__main__':
    app.run(debug=True)