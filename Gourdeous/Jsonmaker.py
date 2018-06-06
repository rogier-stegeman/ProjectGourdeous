from mysql import connector

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
    cur = con.cursor(buffered=True)
    #zorgt voor de startID van de organismes
    cur.execute('''
                SELECT SearchID
                FROM Search
                WHERE SearchID = (
                SELECT MIN( SearchID )
                FROM Search )
                ''')
    c = cur.fetchone()
    counter= c[0]
    counterOrganism = 0
    #opent een Jsonfile in de Flask directory
    file = open("/home/owe8_pg9/public_html/Gourdeous/static/js/Jason.json", "wb")#File word geopend om de data in weg te schrijven
    #SQL statement voor selecteren van de organismes uit de database
    cur.execute('''
                SELECT *
                FROM Organism
                ''')
    c = cur.fetchall()
    #schrijft het organisme voor de binnenste  cirkel
    file.write('''{"name": "Organism","children": [{''')
    e = True
    #Het aantal organismen in de database is de eerste iteratie
    for elements in c:
        #constructie om te zorgen dat de eerste entry geen komma aan het begin heeft
        if e == True:
            file.write('''"name":"%s","children":[{''' % c[counterOrganism][1])
            e = False
        else:
            file.write(''',{"name":"%s","children":[{''' % c[counterOrganism][1])
        #selecteert alle search waarden en zet deze in de lijst
        cur.execute('''
                    SELECT Keyword
                    FROM Search
                    WHERE OrganismID_ID=%s
                    ''', (c[0][0],))
        keywords = cur.fetchall()
        #Deze loop itereert over de keywords in de database
        w = True
        for word in keywords:
            #nogmaals dezelfde constructie
            #schrijft de naam van de search naar de Json
            if w == True:
                file.write('''"name": "%s","children":[{''' % word)
                w = False
            else:
                file.write(''',{"name": "%s","children":[{''' % word)
            cur.execute('''
                        SELECT Terms_found_TermsID
                        FROM Search_Terms_Found
                        WHERE Search_SearchID=%s
                        ''', (counter,))
            counter += 1
            terms = cur.fetchall()
            # deze constructie zorgt voorhet feit dat er bij de eerste entry geen komma geplaatsd word
            #Deze loop itereert over de compounds in de database
            t = True
            articleslist = []
            compounds = []
            #Itereert over de compounds bij de search term
            for termID in terms:
                #selecteert de bijhorende term
                cur.execute('''
                            SELECT Terms
                            FROM Terms_found
                            WHERE TermsID=%s
                            ''', (termID[0],))
                term = cur.fetchone()
                #wanneer term niet in de lijst zit
                if term[0] not in compounds:
                    compounds.append(term[0])
                    cur.execute('''
                                                SELECT TermsID
                                                FROM Terms_found
                                                WHERE Terms=%s
                                                ''', (term[0],))
                    termsID = cur.fetchone()
                    cur.execute('''
                                                SELECT Articles_ArticleID
                                                FROM Articles_Terms
                                                WHERE Terms_found_TermsID=%s
                                                ''', (termsID[0],))
                    articles = cur.fetchall()
                    # Deze loop itereert over de artikelen in de database
                    a = True
                    articlelist = []
                    for ID in articles:
                        cur.execute('''
                                                    SELECT Pubmed_ID, Article_name
                                                    FROM Articles
                                                    WHERE ArticleID=%s
                                                    ''', (ID[0],))
                        article = cur.fetchone()
                        articlelist.append(article)
                    articleslist.append(articlelist)
                else:
                    indexarticles = compounds.index(term[0])
                    cur.execute('''
                                 SELECT TermsID
                                 FROM Terms_found
                                 WHERE Terms=%s
                                 ''', (term[0],))
                    termsID = cur.fetchone()
                    cur.execute('''
                                 SELECT Articles_ArticleID
                                 FROM Articles_Terms
                                 WHERE Terms_found_TermsID=%s
                                 ''', (termsID[0],))
                    articles = cur.fetchall()
                    # print(articles)
                    # Deze loop itereert over de artikelen in de database
                    a = True
                    for ID in articles:
                        cur.execute('''
                                     SELECT Pubmed_ID, Article_name
                                     FROM Articles
                                     WHERE ArticleID=%s
                                     ''', (ID[0],))
                        article = cur.fetchone()
                        if article not in articleslist[indexarticles]:
                            articleslist[indexarticles].append(article)

                counterarticles = 0
            #Deze aparte loop is om te voorkomen dat er dubbele compounds bij dezelfde search term  komen te staan
            for compound in compounds:
                #schrijf de compound namen naar de Json
                if t==True:
                    file.write('''"name":"%s","size":%s,"articles":[''' % (compound, len(articleslist[counterarticles])))
                    t=False
                else:
                    file.write(''',{"name":"%s","size":%s,"articles":[''' % (compound, len(articleslist[counterarticles])))
                #Deze loop itereert over de artikelen in de database
                a = True
                for art in articleslist[counterarticles]:
                   #Schrijf de bijhorende artikelen naar de Json 
                    if a==True:
                        file.write('''["%s","https://www.ncbi.nlm.nih.gov/pubmed/%s"]''' % (art[1].replace('"', '').replace(",", ""), art[0].replace('"', '').replace(",", "")))
                        a=False
                    else:
                        file.write(''',["%s","https://www.ncbi.nlm.nih.gov/pubmed/%s"]''' % (art[1].replace('"', '').replace(",", ""), art[0].replace('"', '').replace(",", "")))
                counterarticles+=1
                file.write("]}")
            file.write("]}")
        file.write("]}")
        counterOrganism += 1
    file.write("]}")
    print(c)
    cur.close()
    con.close()
