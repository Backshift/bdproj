import sqlite3

par_path = os.path.dirname(os.path.realpath(__file__))

sql_path = par_path + "\\data\\BD_Project.sqlite"

def get_names():
    with sqlite3.connect(sql_path) as conn:
        cur = conn.cursor()

        cur.execute('''SELECT charname, Selected.actname
                        FROM Selected
                        INNER JOIN Actors ON Selected.actid = Actors.actid
                        INNER JOIN M_Cast ON Selected.movid = M_Cast.movid AND Selected.actid = M_Cast.actid''')
        characters = cur.fetchall() #Format: [(Jean-Luc Picard, Patrick Stewart), (Tyrion Lannister, Peter Dinklage)]
        characters = list(set(characters))

        filtered_names = set() #Format: [(Jean-Luc, MF )]
        for character in characters:
            charname = character[0].split(" ")[0]
            actname = character[1].split(" ")[0]

            cur.execute('''SELECT gender
                            FROM Names
                            WHERE name = ?''', (actname,))
            nameids = cur.fetchall()

            if len(nameids) == 0 or len(nameids) > 1:
                print(actname, "MF")
                actgender = "MF"
            else:
                print(actname, nameids[0][0])
                actgender = nameids[0][0]

            filtered_names.add((charname, actgender))


        for character in filtered_names:
            print(character[1], character[0])
            continue

            for gender in character[1]:
                cur.execute('''SELECT year, counts
                                FROM Year_Data
                                INNER JOIN Names ON Year_Data.nameid = Names.nameid
                                WHERE name = ? AND gender = ?;''', (character[0], gender))
                data = cur.fetchall().sort()
                print(character[0], "Sorted:", data)
                print("\n\n\n\n\n\n\n\n")





if __name__ == '__main__':
    get_names()
