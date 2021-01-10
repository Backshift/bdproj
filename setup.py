def setup_pckges(packages):
    for package in packages:
        if isinstance(package, list):
            try:
                __import__(package[0])
                print("Successfully imported", package[0])
            except ModuleNotFoundError:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package[1]])
        else:
            try:
                __import__(package)
                print("Successfully imported", package)
            except ModuleNotFoundError:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def setup_database():
    import sqlite3
    with sqlite3.connect('BD_Project.sqlite') as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Names(
                nameid TEXT PRIMARY KEY,
                name TEXT, --Name given to Baby
                gender TEXT);
                ''')
        conn.commit()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Year_Data(
                nameid TEXT,
                counts INTEGER, --How many that Year
                year INTEGER, --Which year this entry was in
                UNIQUE(nameid, year), --Unique constraint to avoid duplicates
                FOREIGN KEY(nameid) REFERENCES Names(nameid));
                ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Actors(
                actid TEXT PRIMARY KEY, --actors imdb id
                actname TEXT); --actors name
            ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Movies(
                movid TEXT PRIMARY KEY, --imdB ID of that movie/series
                title TEXT, --Title of content (e.g. "Star Trek: The Next Generation")
                year INTEGER); --Year of Release or First episode
            ''')
        conn.commit()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Cast(
                movid TEXT,
                actid TEXT,
                FOREIGN KEY(actid) REFERENCES Actors(actid),
                FOREIGN KEY(movid) REFERENCES Movies(movid));
                ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Selected(
                movid TEXT, --imdB ID of that movie/series
                actid TEXT,
                actname TEXT,
                charname TEXT,
                FOREIGN KEY(movid) REFERENCES Movies(movid),
                FOREIGN KEY(actid) REFERENCES Actors(actid));
            ''')
        conn.commit()

if __name__ == "__main__":
    inp = input("This Script will install needed packages by using the pip command.\nProceed? (y/n)\n").strip(",.- ")
    while 1:
        if inp == "y" or inp == "Y":
            needed_packages = ['wheel', 'requests', 'urllib', 'ssl', 'json', 're', ['sqlite3', 'pysqlite'], 'concurrent.futures', 'multiprocessing', 'threading', 'joblib', 'os', 'math', 'datetime', 'time', 'numpy', 'pandas', 'plotly', 'dash', ['progressbar', 'progressbar2']]
            setup_pckges(needed_packages)
            break
        elif inp == "n" or inp == "N":
            print("The Code to execute wont work without these libraries. Exiting...")
            exit()
        else:
            inp = input("Try again:\n")
    print("Setting up database")
    setup_database()
