from mysql import connector

'''
Name: Chemicals.py
Author: Mark de Korte
Function: Reads a list of known plant components and puts them in a Database
'''
def main():
    #Main methode waar de 2 methodes worden aangeroepen
    vullen(Inlezen())

def Inlezen():
    #This function reads a file with a known location and returns it.
    try:
        names = []
        with open('chemicals.csv', 'r') as indata:#open het bestand
            lines = indata.read().split("\n")
        print(len(lines))
        for line in lines[1:]:
            l=line.split(",")#split de chemicalien op komma
            if len(l) >= 6 and len(l[6]) >=5 :#cutoff van chemicalie lengtie
                names.append(l[6].replace("\"", ""))
        return names
    except FileNotFoundError:
        print("Bestand is niet gevonden")

def vullen(names):
    #This function takes chemical names and inserts them into the database
    try:#maak verbindin met de database
        conn = connector.connect(
            user="owe8_pg9",
            password="blaat1234",
            host="localhost",
            database="owe8_pg9")
    except mysql.connector.Error as err:
        print("Kon geen verbinding maken met de database")

    cursor = conn.cursor()
    #MySQL statement for the database
    cursor.execute('''
        INSERT INTO `Chemicals`(`chemical_name`)
        VALUES(%r); 
        ''' % (tuple(names)))
    conn.commit()#sluiten cursor + connectie
    cursor.close()
    conn.close()
    print("Database gevuld")

main()