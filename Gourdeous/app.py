from flask import Flask, render_template, url_for, request, redirect
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

@app.route('/textmine', methods=['POST'])
def submitter():
   # if request.method == 'POST':
    #    if request.form['submit'] == 'submitter':
            plant = request.form['search1']
            health = request.form['search2']
            email = request.form['search3']
            zoekwoorden = plant + " AND " + health
            conn = mysql.connector.connect(user='owe8_pg9', password='blaat1234',
                                           host="localhost",
                                           database='owe8_pg9')
            Chemicals = []
            cur = conn.cursor()
            cur.execute('''
                        SELECT chemical_name FROM Chemicals  
                        ''')
            chemical = cur.fetchone()
            while chemical is not None:
                print(chemical[0])
                Chemicals.append(chemical[0])
                chemical = cur.fetchone()

            print(len(Chemicals))
            # id_search = uuid.uuid4()
            cur.execute('''
                              INSERT INTO `Search`( `Keyword`)
                             VALUES(%s );
                             ''', (zoekwoorden,))
            keyword = 'Toxine'
            # zoekt de synoniemen van de opgegeven keywords
            # synonyms =[]
            # for syn in wordnet.synsets(keyword):
            # for l in syn.lemmas():
            # synonyms.append(l.name())
            keyword2 = 'is'
            Entrez.email = "damian.bolwerk@gmail.com"  # Always tell NCBI who you are
            handle = Entrez.esearch(db="pubmed", term=zoekwoorden, usehistory="y")
            record = Entrez.read(handle)
            webenv1 = record["WebEnv"]
            query_key1 = record["QueryKey"]
            idlist = record["IdList"]
            count = int(record["Count"])
            print("Found %i results" % count)
            batch_size = 100
            for start in range(0, count, batch_size):
                end = min(count, start + batch_size)
                print("Going to download record %i to %i" % (start + 1, end))
                attempt = 1
                # while attempt <= 3:
                try:
                    fetch_handle = Entrez.efetch(db="pubmed",  # term ="keyword",
                                                 retmode="text", retstart=start,
                                                 retmax=batch_size, rettype="medline",
                                                 webenv=webenv1, query_key=query_key1)
                    # if attempt == 3:...

                # except HTTPError as err:
                #     if 500 <= err.code <= 599:
                #          print("Received error from server %s" % err)
                #          print("Attempt %i of 3" % attempt)
                #          attempt += 1
                #          time.sleep(15)
                except:
                    raise
            data = Medline.parse(fetch_handle)
            data_list = list(data)
            for record in data_list:
                opslag_record = []
                opslag_compound = []
                title = str(record.get("TI", "null"))
                abstract = str(record.get("AB", "null"))
                fuse = title + abstract
                pubmedID = str(record.get("PMID", "null"))
                taal = str(record.get("LA", "null"))
                author = str(record.get("AU", "null"))
                article_date = str(record.get("DP", "null"))
                for plant_compound in Chemicals:
                    print(plant_compound)
                    # print("lol")
                    if plant_compound.lower() in fuse.lower():
                        # print("lol")
                        if len(opslag_record) == 0:
                            opslag_record.append(record)
                            cur.execute('''
                              INSERT INTO `Articles`(`Pubmed_ID`, `Article_name`, `Article_author`, `Article_year`,`Article_language`)
                             VALUES(%s, %s, %s, %s, %s);
                             ''', (pubmedID, title, author, article_date, taal))
                        cur.execute('''
                            SELECT ArticleID FROM Articles
                            WHERE Pubmed_ID=%s
                            ''', (pubmedID,))
                        article_id = cur.fetchone()
                        cur.execute('''
                               INSERT INTO `Terms_found`(`Terms`)
                               VALUES(%s);
                                ''', (plant_compound,))
                        cur.execute('''
                            SELECT TermsID FROM Terms_found
                            WHERE Terms=%s
                            ''', (plant_compound,))
                        terms_id = cur.fetchone()
                        cur.execute('''
                               INSERT INTO `Articles_Terms`(`Terms_found_TermsID`, `Articles_ArticleID`)
                               VALUES(%s, %s);
                                ''', (terms_id, article_id))
                        # opslag_compound.append(plant_compound)
            conn.commit()
            cur.close()
            conn.close()
            return render_template("Busy.html")
  #  elif request.method == ['GET']:
   #     return render_template("textmine.html")
   # else:
   #     return render_template("textmine.html")


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