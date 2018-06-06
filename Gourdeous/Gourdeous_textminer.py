# Gourdeous textminer heeft als functionaliteit om met behulp Entrez Programming Utilities (E-utilities)
# pubmed artikelen op te halen die de 2 opgegeven keywords bevatten en kijkt of de artikelen bepaalde plant compounds bevatten.
# deze plant compounds staan opgeslagen in de Gourdeous database.
# De artikelen die 1 of meer van deze compounds bevatten worden opgeslagen in de Gourdeous textminer samen met de gevonden compounds.
# Op basis van wat er in de database staat wordt er een jsonfile gemaakt die gebruikt wordt om de zoekresultaten
# te visualiseren in de sunburst.

#Author: Damian,Mark

# De nodige importaties voor het textminning
import time
from Bio import Entrez
from Bio import Medline
import urllib2
import mysql.connector
import MySQLdb as my
import sys

# De functies die worden uitgevoert als er op de website op de textmine knop wordt gedrukt
def main(organisme,zoekwoord,email):
    data = entrez_search(organisme,zoekwoord,email)
    con = connector()
    db_vullen(data,organisme,zoekwoord,con)

# Maakt een connectie met de database waar de textmining resultaten worden opgeslagen.
def connector():
    try:
         conn = mysql.connector.connect(user='owe8_pg9', password='blaat1234',
                                   host='localhost',
                                   database='owe8_pg9')
         return conn
    except my.Error as e:
        print(e)

    except:
        print("Unknown error occurred")

# Zoekt artikelen in de pubmed database die de ingevulde keywords bevatten
# met behulp van de Entrez Programming Utilities (E-utilities).
def entrez_search(plant_name,health_benefit,email_adress):
    plant = plant_name
    health_effect = health_benefit
    query = plant + " AND " + health_effect
    Entrez.email = email_adress   # Always tell NCBI who you are
    # zoekt de artikel id van de artikelen die de opgegeven termen bevatten en slaat deze op in een web enviroment.
    handle = Entrez.esearch(db="pubmed", term= query ,  usehistory="y")
    record = Entrez.read(handle)
    webenv1=record["WebEnv"]
    query_key1=record["QueryKey"]
    count = int(record["Count"])# kijkt hoeveel artikelen zijn gevonden.
    print("Found %i results" % count)
    batch_size = 100
    # download de artikelen per 100 die in de opgegeven web enviroment staan.
    for start in range(0,count,batch_size):
        end = min(count, start+batch_size)
        print("Going to download record %i to %i" % (start+1, end))
        attempt = 1

    try:
        fetch_handle = Entrez.efetch(db="pubmed",
                                     retmode="text",retstart=start,
                                     retmax=batch_size,rettype= "medline",
                                     webenv=webenv1,query_key=query_key1)

    # stopt de applicatie als er 3 HTTPErrors zijn opgetreden en vertelt de gebruiker
    # dat het later opnieuwe geprobeerd moet worden.
    except urllib2.HTTPError as err:
        if 500 <= err.code <= 599:
             print("Received error from server %s" % err)
             print("Attempt %i of 3" % attempt)
             attempt += 1
             if attempt == 4:
                 sys.exit("more then 3 HTTPError have occured , terminating application ")
                 time.sleep(15)
        else:
           raise
    # lijst van opgehaalde artikelen.
    data = Medline.parse(fetch_handle)
    data_list = list(data)
    fetch_handle.close()
    return data_list

# Stopt de zoektermen in de database
# haalt een lijst van plant compounds op uit de database en kijkt welke compounds er in de artikelen voorkomen
# slaat de artikelen en de compounds die erin voorkomen op in de database.
def db_vullen(artikelen,organisme,zoekwoord, conn):
    try:
        Chemicals=[]
        cur = conn.cursor(buffered=True)
        #Deze SQL query haalt alle compounds op uit de database
        cur.execute('''
                    SELECT chemical_name FROM Chemicals  
                    ''')
        chemical = cur.fetchone()
        while chemical is not None:
            Chemicals.append(chemical[0])
            chemical = cur.fetchone()
        #SQL query voor het ophalen van alle organismen in de database
        cur.execute('''
                    SELECT OrganismID FROM Organism
                    WHERE Organism=%s
                    ''', (organisme,))
        organismID = cur.fetchone()
        if organismID == None:
            #als huidig organisme niet bekend is: maak een nieuwe rij met het organisme
            cur.execute('''
                        INSERT INTO `Organism`( `Organism`)
                        VALUES(%s);
                             ''', (organisme,))
            conn.commit()
            #Selecteer de ID van het toegevoegde organisme
            cur.execute('''
                        SELECT OrganismID FROM Organism
                        WHERE Organism=%s
                        ''', (organisme,))
            organismID = cur.fetchone()
        #Insert de search term bij het bijhorende organisme
        cur.execute('''
                          INSERT INTO `Search`( `Keyword`,`OrganismID_ID`)
                         VALUES(%s, %s);
                         ''', (zoekwoord, organismID[0]))
        conn.commit()
        #Kijk of de search term al in de database is toegevoegd
        cur.execute('''
                    SELECT SearchID FROM Search
                    WHERE Keyword=%s AND OrganismID_ID=%s
                    ''', (zoekwoord, organismID[0]))
        c = cur.fetchone()
        if c == None:
            SearchID = 0
        else:
            SearchID = c[0]
        #Zorgt voor de juiste StartID van de artikelen
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
        #Zorgt voor de juiste TermsID van de compounds
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

        # gaat de artikelen langs en haalt per artikel de titel,abstract,pubmedID,taal van artikel,auteur en publicatie datum op.
        for record in artikelen:
            added = False
            title = str(record.get("TI", "null"))
            abstract = str(record.get("AB", "null"))
            # voegt de titel en abstract samen zodat er gekeken kan worden
            # of bepaalde plant compounds erin aanwezig zijn.
            mine_data = title + abstract
            pubmedID = str(record.get("PMID", "null"))
            taal = record.get("LA", "null")[0]
            author = record.get("AU", "null")[0]
            article_date = str(record.get("DP", "null"))
            for plant_compound in Chemicals:
                #Itereert over de opgehaalde compounds
                if plant_compound.lower() in mine_data.lower() and len(plant_compound) > 1:
                    #Wanneer de compound voorkomt in de titel of abstract
                    if added == False:
                        #Kijkt of het artikel al in de database voorkomt om redundantie te voorkomen
                        cur.execute('''
                                        SELECT ArticleID
                                        FROM Articles
                                        WHERE Pubmed_ID =%s
                                        ''', (pubmedID,))
                        c = cur.fetchone()
                        if c == None:
                            #Wanneer het artikel niet voorkomt insert het artikel met de getextminede data
                            counter += 1
                            cur.execute('''
                                  INSERT INTO `Articles`(`ArticleID`, `Pubmed_ID`, `Article_name`, `Article_author`, `Article_year`,`Article_language`)
                                 VALUES(%s, %s, %s, %s, %s, %s);
                                 ''', (counter, pubmedID, title, author, article_date, taal))
                            added = True
                            article_id = counter
                        else:
                            article_id = c[0]
                    #Kijk of de term al voorkomt in de daatabase
                    cur.execute('''
                            SELECT TermsID FROM Terms_found
                            WHERE Terms=%s
                            ''', (plant_compound,))
                    terms_id = cur.fetchone()
                    if terms_id == None:
                        #Wanneer de term nog niet bekend is: Voeg het toe
                        idcounter += 1
                        cur.execute('''
                                   INSERT INTO `Terms_found`(`TermsID`, `Terms`)
                                   VALUES(%s, %s);
                                    ''', (idcounter, plant_compound))
                        #Zet de zojuist toegevoegde term in de tussentabel
                        cur.execute('''
                                   INSERT INTO `Articles_Terms`(`Terms_found_TermsID`, `Articles_ArticleID`)
                                   VALUES(%s, %s);
                                    ''', (idcounter, article_id))
                        #Bekijk of de compound al aan de Search term is gebonden
                        cur.execute('''
                                SELECT * FROM Search_Terms_Found
                                WHERE `Search_SearchID`=%s AND `Terms_found_TermsID`=%s
                                ''', (SearchID, idcounter))
                        c = cur.fetchone()
                        #Als de term nog niet is toegevoegd:
                        if c == None:
                            # Zet de zojuist toegevoegde term in de tussentabel tussen het zoekwoord en de term
                            cur.execute('''
                                    INSERT INTO `Search_Terms_Found`(`Search_SearchID`, `Terms_found_TermsID`)
                                    VALUES(%s, %s);
                                    ''', (SearchID, idcounter))
                    #Als de term al is toegevoegd:
                    else:
                        #insert met de zojuist opgevraagde ID
                        cur.execute('''
                                   INSERT INTO `Articles_Terms`(`Terms_found_TermsID`, `Articles_ArticleID`)
                                   VALUES(%s, %s);
                                    ''', (terms_id[0], article_id))
                        #Selecteer de juiste ID voor de term + compound
                        cur.execute('''
                                SELECT * FROM Search_Terms_Found
                                WHERE `Search_SearchID`=%s AND `Terms_found_TermsID`=%s
                                ''', (SearchID, idcounter))
                        c = cur.fetchone()
                        #wanneer de entry nog bestaat:
                        if c == None:
                            #Insert the Searchterm met de bijhorende compound
                            cur.execute('''
                                    INSERT INTO `Search_Terms_Found`(`Search_SearchID`, `Terms_found_TermsID`)
                                    VALUES(%s, %s);
                                    ''', (SearchID, terms_id[0]))
                    conn.commit()
    # errors die kunnen optreden bij het bewerken van de database.
    except my.DataError as e:
        print("DataError")
        print(e)

    except my.InternalError as e:
        print("InternalError")
        print(e)

    except my.IntegrityError as e:
        print("IntegrityError")
        print(e)

    except my.OperationalError as e:
        print("OperationalError")
        print(e)

    except my.NotSupportedError as e:
        print("NotSupportedError")
        print(e)

    except my.ProgrammingError as e:
        print("ProgrammingError")
        print(e)


    except Exception as e:
        print(e)
        print("Unknown error occurred")

    finally:
        cur.close()
        conn.close()
    






