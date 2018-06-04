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
zoekwoord = "diabetis"
organisme = "dioscorea batatas"
conn = mysql.connector.connect(user='owe8_pg9', password='blaat1234',
                                    host="localhost",
                                    database='owe8_pg9')
zoekwoorden = organisme + " AND " + zoekwoord
Chemicals=[]
cur = conn.cursor(buffered=True)
cur.execute('''
            SELECT chemical_name FROM Chemicals  
            ''')
chemical = cur.fetchone()
while chemical is not None:
    print(chemical[0])
    Chemicals.append(chemical[0])
    chemical = cur.fetchone()

print(len(Chemicals))
cur.execute('''
            SELECT OrganismID FROM Organism
            WHERE Organism=%s
            ''', (organisme,))
organismID = cur.fetchone()
if organismID == None:
    cur.execute('''
                INSERT INTO `Organism`( `Organism`)
                VALUES(%s);
                     ''', (organisme,))
    conn.commit()
    cur.execute('''
                SELECT OrganismID FROM Organism
                WHERE Organism=%s
                ''', (organisme,))
    organismID = cur.fetchone()

cur.execute('''
                  INSERT INTO `Search`( `Keyword`,`OrganismID_ID`)
                 VALUES(%s, %s);
                 ''', (zoekwoord,organismID[0]))
conn.commit()
cur.execute('''
            SELECT SearchID FROM Search
            WHERE Keyword=%s AND OrganismID_ID=%s
            ''', (zoekwoord, organismID[0]))
c = cur.fetchone()
if c == None:
    SearchID = 0
else:
    SearchID = c[0]
# keyword = 'Toxine'
print("XDDDDDDD")
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
print(len(data_list))
cur.execute('''
            SELECT ArticleID
            FROM Articles
            WHERE ArticleID = (
            SELECT MAX( ArticleID )
            FROM Articles )
            ''')
c = cur.fetchone()
if c == None:
    counter = 0
else:
    counter = c[0]
cur.execute('''
            SELECT TermsID
            FROM Terms_found
            WHERE TermsID= (
            SELECT MAX( TermsID )
            FROM Terms_found )
            ''')
c = cur.fetchone()
if c == None:
    idcounter = 0
else:
    idcounter = c[0]

for record in data_list:
    added=False
    opslag_compound = []
    title = str(record.get("TI", "null"))
    abstract = str(record.get("AB", "null"))
    fuse = title + abstract
    pubmedID = record.get("PMID", "null")[0]
    taal = record.get("LA", "null")[0]
    author = record.get("AU", "null")[0]
    article_date = str(record.get("DP", "null"))
    for plant_compound in Chemicals:
        if plant_compound.lower() in fuse.lower() and len(plant_compound) > 1:
            if added==False:
                cur.execute('''
                            SELECT ArticleID
                            FROM Articles
                            WHERE Pubmed_ID =%s
                            ''', (pubmedID,))
                c = cur.fetchone()
                if c == None:
                    counter += 1
                    cur.execute('''
                      INSERT INTO `Articles`(`ArticleID`, `Pubmed_ID`, `Article_name`, `Article_author`, `Article_year`,`Article_language`)
                     VALUES(%s, %s, %s, %s, %s, %s);
                     ''', (counter, pubmedID, title, author, article_date, taal))
                    added = True
                    article_id = counter
                else:
                    article_id = c[0]
            cur.execute('''
                SELECT TermsID FROM Terms_found
                WHERE Terms=%s
                ''', (plant_compound,))
            terms_id = cur.fetchone()
            if terms_id == None:
                idcounter += 1
                cur.execute('''
                       INSERT INTO `Terms_found`(`TermsID`, `Terms`)
                       VALUES(%s, %s);
                        ''', (idcounter, plant_compound))
                cur.execute('''
                       INSERT INTO `Articles_Terms`(`Terms_found_TermsID`, `Articles_ArticleID`)
                       VALUES(%s, %s);
                        ''', (idcounter, article_id))
                cur.execute('''
                    SELECT * FROM Search_Terms_Found
                    WHERE `Search_SearchID`=%s AND `Terms_found_TermsID`=%s
                    ''', (SearchID, idcounter))
                c = cur.fetchone()
                if c == None:
                    cur.execute('''
                        INSERT INTO `Search_Terms_Found`(`Search_SearchID`, `Terms_found_TermsID`)
                        VALUES(%s, %s);
                        ''', (SearchID, idcounter))
            else:
                cur.execute('''
                       INSERT INTO `Articles_Terms`(`Terms_found_TermsID`, `Articles_ArticleID`)
                       VALUES(%s, %s);
                        ''', (terms_id[0], article_id))
                cur.execute('''
                    SELECT * FROM Search_Terms_Found
                    WHERE `Search_SearchID`=%s AND `Terms_found_TermsID`=%s
                    ''', (SearchID, idcounter))
                c = cur.fetchone()
                if c == None:
                    cur.execute('''
                        INSERT INTO `Search_Terms_Found`(`Search_SearchID`, `Terms_found_TermsID`)
                        VALUES(%s, %s);
                        ''', (SearchID, terms_id[0]))
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