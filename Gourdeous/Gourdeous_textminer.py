# De nodige importaties voor het textminning
import time
from Bio import Entrez
from Bio import Medline
from urllib.error import HTTPError  # for Python 3
import mysql.connector
from flask import Flask
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
                                   host='cytosine.nl ',
                                   database='owe8_pg9')
         return conn
    except my.Error as e:
        return(e)

    except:
        print("Unknown error occurred")

# Zoekt artikelen in de pubmed database die de ingevulde keywords bevatten
# met behulp van de Entrez Programming Utilities (E-utilities).
def entrez_search(plant_name,health_benefit,compounds,email_adress):
    plant = plant_name
    health_effect = health_benefit
    query = plant + " AND " + health_benefit
    Entrez.email = email_adress   # Always tell NCBI who you are
    # zoekt de artikel id van de artikelen die de opgegeven termen bevatten en slaat deze op in een web enviroment.
    handle = Entrez.esearch(db="pubmed", term= query  ,  usehistory="y")
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


    except HTTPError as err:
        if 500 <= err.code <= 599:
             print("Received error from server %s" % err)
             print("Attempt %i of 3" % attempt)
             attempt += 1
             if attempt == 4:
                 sys.exit("more then 3 HTTPError have occured , terminating application ")
             time.sleep(15)
        else:
           raise

    data = Medline.parse(fetch_handle)
    data_list = list(data)
    fetch_handle.close()
    return data_list

# Stopt de zoektermen in de database
# haalt een lijst van plant compounds op uit de database en kijkt welke compounds er in de artikelen voorkomen
# slaat de artikelen en de compounds die erin voorkomen op in de database.
def db_vullen(artikelen,plant,health, conn):
    try:
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
                         ''', (zoekwoord, organismID[0]))
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

        # gaat de artikelen langs en haalt per artikel bepaalde informatie eruit zoals de auteurs van het artikel.
        for record in artikelen:
            added = False
            title = str(record.get("TI", "null"))
            abstract = str(record.get("AB", "null"))
            fuse = title + abstract
            pubmedID = str(record.get("PMID", "null"))
            taal = record.get("LA", "null")[0]
            author = record.get("AU", "null")[0]
            article_date = str(record.get("DP", "null"))
            for plant_compound in Chemicals:
                if plant_compound.lower() in fuse.lower() and len(plant_compound) > 1:
                    if added == False:
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
    # errors die kunnen optreden bij het bewerken van de database.
    except my.DataError as e:
        cur.rollback()
        print("DataError")
        print(e)

    except my.InternalError as e:
        cur.rollback()
        print("InternalError")
        print(e)

    except my.IntegrityError as e:
        cur.rollback()
        print("IntegrityError")
        print(e)

    except my.OperationalError as e:
        cur.rollback()
        print("OperationalError")
        print(e)

    except my.NotSupportedError as e:
        cur.rollback()
        print("NotSupportedError")
        print(e)

    except my.ProgrammingError as e:
        cur.rollback()
        print("ProgrammingError")
        print(e)

    except:
        print("Unknown error occurred")

    finally:
        cur.close()
        conn.close()
