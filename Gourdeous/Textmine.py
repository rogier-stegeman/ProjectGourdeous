import time
from flask import Flask
# De nodige importaties voor het textminning
from Bio import Entrez
#from nltk.corpus import wordnet
from Bio import Medline
#from urllib.error import HTTPError  # for Python 3
#from nltk.misc import babelfish
import mysql.connector
#import uuid

#app = Flask(__name__)
health_effect =..
plant = ..
mail =.
zoekwoorden = "bitter gourd" + " AND " + "antidiabetic"
conn = mysql.connector.connect(user='owe8_pg9', password='blaat1234',
                                    host="localhost",
                                    database='owe8_pg9')
Chemicals=[]
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
#id_search = uuid.uuid4()
cur.execute('''
                  INSERT INTO `Search`( `Keyword`)
                 VALUES(%s );
                 ''', (zoekwoorden,))
keyword = 'Toxine'
# zoekt de synoniemen van de opgegeven keywords
#synonyms =[]
#for syn in wordnet.synsets(keyword):
#for l in syn.lemmas():
# synonyms.append(l.name())
keyword2 = 'is'
Entrez.email = "damian.bolwerk@gmail.com"     # Always tell NCBI who you are
handle = Entrez.esearch(db="pubmed", term= zoekwoorden ,  usehistory="y")
record = Entrez.read(handle)
webenv1=record["WebEnv"]
query_key1=record["QueryKey"]
idlist = record["IdList"]
count = int(record["Count"])
print("Found %i results" % count)
batch_size = 100
for start in range(0,count,batch_size):
    end = min(count, start+batch_size)
    print("Going to download record %i to %i" % (start+1, end))
    attempt = 1
    # while attempt <= 3:
    try:
        print("hoi")
        fetch_handle = Entrez.efetch(db="pubmed",#term ="keyword",
                                 retmode="text",retstart=start,
                                 retmax=batch_size,rettype= "medline",
                                 webenv=webenv1,query_key=query_key1)
        #if attempt == 3:...

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
            #print("lol")
            if len(opslag_record)== 0:
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
            #opslag_compound.append(plant_compound)
conn.commit()
cur.close()
conn.close()






#try:
    #cur.execute('''
      #  INSERT INTO `Articles`(`ArticleID`, `Article_name`, `Article_author`, `Article_year`,'Article_lang')
        #VALUES(pubmedID, title, author, article_date,taal);
      # ''')
   # conn.commit()
#except:
   # conn.rollback()
#conn.close()

#@app.route("/")
#def test():
    #return "hoi"

# if __name__ == "__main__":
#     app.run(debug=True)