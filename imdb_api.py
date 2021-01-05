import requests
import sqlite3

url = "https://imdb8.p.rapidapi.com/actors/get-all-filmography"

querystring = {"nconst":"nm0227759"}

headers = {
    'x-rapidapi-key': "872ca16690msh82ba390ec27f560p17743ajsn483ac825d272",
    'x-rapidapi-host': "imdb8.p.rapidapi.com"
    }

resp = requests.request("GET", url, headers=headers, params=querystring)

try:
    js = resp.json()
    print(js)
    with open("D:\\Drive\\OTH\\Big Data Analytics\\Project\\bdproj\\imdb_feedback.txt", mode='w') as fh:
        fh.write(resp.text)
    
except:
    print("ERROR")
    print(resp.text)
