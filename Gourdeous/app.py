from flask import Flask, render_template, url_for, request

app = Flask(__name__)
#app = Flask(__name__)
wsgi_app = app.wsgi_app
#print(open("templates/home.html","r").read())


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/sunburst')
def sunburst():
    return render_template("sunburst.html")


@app.route('/help')
def helppage():
    return render_template("help.html")


if __name__ == '__main__':
    app.run(debug=True)