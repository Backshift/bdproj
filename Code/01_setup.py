import os
par_path = os.path.dirname(os.path.realpath(__file__))
sql_path = par_path + "\\data\\BD_Project.sqlite"


def setup_pckges(packages):
    import subprocess
    import sys
    print("Updating pip...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', "--upgrade", "pip"])

    for package in packages:
        if isinstance(package, list):
            packname = package[0]
            packimport = package[1]
        else:
            packname = package
            packimport = package

        try:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', packimport])
            except:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--user', packimport])
                except:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', packimport])
            __import__(packname)
            print("Successfully imported", packname, "\n\n")
        except:
            print("Failed to import", packname, "\n\n")

def setup_database():
    import sqlite3
    import os
    print("Setting up database")
    datapath = par_path+"\\data\\"
    if not os.path.exists(datapath):
        os.makedirs(datapath)

    with sqlite3.connect(sql_path) as conn:
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
            CREATE TABLE IF NOT EXISTS M_Cast(
                movid TEXT,
                actid TEXT,
                charname TEXT,
                FOREIGN KEY(actid) REFERENCES Actors(actid),
                FOREIGN KEY(movid) REFERENCES Movies(movid),
                UNIQUE (movid, actid));
                ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Selected(
                movid TEXT, --imdB ID of that movie/series
                actid TEXT,
                actname TEXT,
                chargender TEXT,
                FOREIGN KEY(movid) REFERENCES Movies(movid),
                FOREIGN KEY(actid) REFERENCES Actors(actid),
                UNIQUE(movid, actname));
            ''')
        conn.commit()

def download_files(files):
    import requests
    import os
    import progressbar
    import time
    i=1
    for file in files:
        filepath = par_path + file['path']
        fullpath = filepath + file['name']
        try:
            if not os.path.exists(filepath):
                os.makedirs(filepath)
        except OSError:
            print ('Error: Creating directory. ' +  filepath)

        if os.path.isfile(fullpath):
            try:
                r = requests.head(file['url'])
            except:
                print("Could reach adress:", file['url'], "Please check URL.\nExiting.")
                exit()
            filetime_net = time.strptime(r.headers['last-modified'], "%a, %d %b %Y %H:%M:%S %Z")
            filetime_drive = time.gmtime(os.path.getmtime(fullpath))

        if os.path.isfile(fullpath) and filetime_drive >= filetime_net:
                print("Local file represents the latest version. Not downloading file. Continuing.")
        else:
           print('Downloading data file ('+str(i)+"/"+str(len(files))+").\nCheck Task-Manager for Network activity.\n" )
           with progressbar.ProgressBar(widgets=[progressbar.Bar()],max_value=3,) as bar:
               bar.update(int(1), force=True)
               try:
                   r = requests.get(file['url'], allow_redirects=True, stream=True)
               except:
                   print("Could not download file:", file['url'], "\nExiting.")
                   exit()
               bar.update(int(2), force=True)
               open(fullpath, 'wb').write(r.content)
               bar.update(int(3), force=True)

        print("Decompressing File("+str(i)+"/"+str(len(files))+").")

        with progressbar.ProgressBar(widgets=[progressbar.Bar()],max_value=2,) as bar:
            name_cut = file['name'].split(".")
            bar.update(int(1), force=True)

            if name_cut[(len(name_cut)-1)] == "gz":
                import gzip

                newname=""
                for i in range(0, len(name_cut)-1):
                    newname+=name_cut[i]
                    if i <= len(name_cut)-2:
                        newname+="."

                with gzip.open(fullpath, 'rb') as f:
                    file_content = f.read()
                open(filepath+newname, 'wb').write(file_content)
                bar.update(int(2), force=True)
            elif name_cut[(len(name_cut)-1)] == "zip":
                import zipfile
                with zipfile.ZipFile(fullpath, 'r') as z:
                    z.extractall(filepath)
                bar.update(int(2), force=True)
        i+=1

if __name__ == "__main__":
    inp = input("The following Code will install needed packages by using the pip command.\nProceed? (y/n)\n").strip(",.- ")
    while 1:
        if inp == "y" or inp == "Y":
            needed_packages = ['wheel', 'requests', 'joblib', 'datetime', 'pandas', 'plotly', 'dash', ['progressbar', 'progressbar2'], 'numpy']
            setup_pckges(needed_packages)
            break
        elif inp == "n" or inp == "N":
            print("The Code to execute wont work without these libraries. Exiting...")
            exit()
        else:
            inp = input("Try again:\n")
    setup_database()

    files = [
            {'url': "https://www.ssa.gov/OACT/babynames/names.zip",
            'path': "\\data\\Names_USA\\",
            'name': "names.zip"},
            {'url': "https://datasets.imdbws.com/name.basics.tsv.gz",
             'path': "\\data\\Names_ImdB\\",
             'name': "name.basics.tsv.gz"}
             ]
    download_files(files)
