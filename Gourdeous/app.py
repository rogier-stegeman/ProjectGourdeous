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

@app.route('/textmine')
def textmine():
    organisms = ['bitter gourd', 'yam', 'Momordica charantia', 'Dioscorea batatas']
    compounds = ['fatty acid', 'insulin', 'cholesterol', 'sugar', 'glucose', 'vitamin A', 'vitamin B', 'vitamin C',
                 'vitamin E', 'calcium', 'iron', 'potassium']
    health_effects = ['diabetes', 'cancer', 'weigth loss', 'cough', 'wounds', 'rheumatism', 'laxative', 'diarrhea',
                      'abdominal pain', 'fever', 'hypoglycemia', 'urinary incontinence', 'chest pain', 'miscarriage']
    return render_template('textmine.html', organisms=organisms, compounds=compounds, health_effects=health_effects)

@app.route('/textmine', methods=['POST'])
def submitter():
    plant = request.form['search1']
    health = request.form['search2']
    email = request.form['search3']
    
    return render_template('textmine.html', plant=plant, health=health, email=email )

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