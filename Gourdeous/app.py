from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!!!!'


@app.route('/sunburst')
def sunburst():
    return render_template("Sunburst.html")


if __name__ == '__main__':
    app.run()
