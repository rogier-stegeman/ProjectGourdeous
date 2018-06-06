from flask import Flask
#import mysql.connector

app = Flask(__name__)
wsgi_app = app.wsgi_app

@app.route('/')
def ID_checken_headers():
    # conn = mysql.connector.connect(
    #     host="127.0.0.1",
    #     user="owe8_pg9",
    #     db="owe8_pg9",
    #     password="blaat1234")
    # cursor = conn.cursor()
    # cursor.execute("""SELECT OrganismID FROM Organism""")
    # inhoud = cursor.fetchall()
    # cursor.close()
    # conn.close()
    # print(inhoud)
    # return inhoud
    return "HELLO"


if __name__ == '__main__':
    app.run(debug=True)

