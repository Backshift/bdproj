import requests
import sqlite3
import pandas as pd
import concurrent.futures

conn = sqlite3.connect('BD_Project.sqlite')
cur = conn.cursor()
cur.execute("SELECT MAX(rowid) FROM Selected_Actors")
nr_entries = cur.fetchall()
conn.close()



def get_saved_actor(rowid):
    conn = sqlite3.connect('BD_Project.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Selected_Actors WHERE rowid = ?", rowid)
    act_entry = cur.fetchall()
    conn.close()

    return act_entry

def check_db_entries(act_entry):

    act_name = act_entry[1]
    act_name = act_name.replace(" ", "_")

    conn = sqlite3.connect('BD_Project.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?;", act_name)
    act_entry = cur.fetchall()
    conn.close()

    if act_entry != 0:
        return True
    else:
        return False



























def get_imdb_data(act_entry):
    apiurl = "https://imdb8.p.rapidapi.com/actors/get-all-filmography"

    querystring = {"nconst":"nm0001772"}

    headers = {
        'x-rapidapi-key': "872ca16690msh82ba390ec27f560p17743ajsn483ac825d272",
        'x-rapidapi-host': "imdb8.p.rapidapi.com"
        }

    resp = requests.request("GET", apiurl, headers=headers, params=querystring)

    try:
        js = resp.json()
        print(js)
        with open("D:\\Drive\\OTH\\Big Data Analytics\\Project\\bdproj\\imdb_feedback.txt", mode='w') as fh:
            fh.write(resp.text)
    except:
        print("ERROR")
        print(resp.text)

    return act_filmography

























def save_imdb_data(act_entry, act_filmography):
    pass

































conn = sqlite3.connect('BD_Project.sqlite')
cur.execute("SELECT MAX(rowid) FROM Selected_Actors")
nr_entries = cur.fetchall()
conn.close()

i=1
while i <= nr_entries:
    act_entry = get_saved_actor(i)
    existing = check_db_entries(act_entry)
    if existing == False:
        act_filmography = get_imdb_data(act_entry)
        save_imdb_data(act_entry, act_filmography)
    i += 1
