import mysql.connector
'''
Name: Jsonmaker.py
Author: Mark de Korte
Function:
Selects data from the database and puts it in Json format for the visualisation
'''
def main():
    Inlezen(Connection())

def Connection():
    #Maakt een connectie met de database
    try:
        conn = connector.connect(
            user="owe8_pg9",
            password="blaat1234",
            host="localhost",
            database="owe8_pg9")
    except mysql.connector.Error as err:
        print("Kon geen verbinding maken met de database")
    return conn

def Inlezen(con):
    #Functie om de data uit de database te halen en in Json formaat te parsen.
    counter=0
    file = open("Jason.json", "wb")#File word geopend om de data in weg te schrijven
    cur = con.cursor(buffered=True)
    #SQL statement voor selecteren van de organismes uit de database
    cur.execute('''
                SELECT *
                FROM Organism
                ''')
    c = cur.fetchall()
    file.write('''{"name": "Organism","children": [{''')
    e = True
    #Het aantal organismen in de database is de eerste iteratie
    for elements in c:
        if e == True:
            file.write('''"name":"%s","Children":[{''', (c[0][1]))
        else:
            file.write('''",name":"%s","Children":[{''', (c[0][1]))
        cur.execute('''
                    SELECT Keyword,
                    FROM Search
                    WHERE OrganismID_ID=%s
                    ''', (c[0][0]))
        keywords = cur.fetchall()
        w = True
        #Deze loop itereert over de keywords in de database
        for word in keywords:
            counter += 1
            if w == True:
                file.write('''"name": "%s","children":[{''')
                w = False
            else:
                file.write(''',"name": "%s","children":[{''')
            cur.execute('''
                        SELECT Terms_found_TermsID,
                        FROM Search
                        WHERE Search_SearchID=%s
                        ''', (counter,))
            terms = cur.fetchall()
            t = True# deze constructie zorgt voorhet feit dat er bij de eerste entry geen komma geplaatsd word
            #Deze loop itereert over de compounds in de database
            for term in terms:
                if t==True:
                    file.write('''"name":%s,"size":%s,"articles":[''', (term, 100))
                    t==False
                else:
                    file.write('''",name":%s,"size":%s,"articles":[''', (term, 100))
                cur.execute('''
                            SELECT Articles_ArticleID,
                            FROM Articles_Terms
                            WHERE Terms_found_TermsID=%s
                            ''', (term,))
                articles = cur.fetchall()
                #Deze loop itereert over de artikelen in de database
                for ID in articles:
                    cur.execute('''
                                SELECT Pubmed_ID, Article_name,
                                FROM Articles
                                WHERE ArticleID=%s
                                ''', (ID,))
                    articles = cur.fetchall()
                    a=True
                    for  article in articles:
                        if a==True:
                            file.write('''["%s","www.pubmed.gov/%s",%s]''')
                            a==False
                        else:
                            file.write(''',["%s","www.pubmed.gov/%s",%s]''')
                file.write("]}")
            file.write("]}")
        file.write("]}")
    file.write("]}")
    print(c)
    cur.close()
    con.close()





main()