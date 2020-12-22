import urllib.request, urllib.parse, urllib.error
import json
import ssl
import time
import re
import datetime
import sqlite3

def getStapiCharData():

    serurl = 'http://stapi.co/api/v1/rest/character/search?' # API URL

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    all = list() # List for all recieved STAPI data, for return use
    last=False
    i=0
    parms = dict() # Parameters to give the API (e.g. PageNumber)

    while last == False: # Collect data until API states 'lastPage'
        parms['pageNumber'] = i
        url = serurl + urllib.parse.urlencode(parms) + '&pretty' # Encode URL to send to API
        print('Retrieving', url)
        uh = urllib.request.urlopen(url, context=ctx) # Send API request
        data = uh.read().decode() # Decode recieved Data (UTF-8? -> UNICODE)

        try:
            st = json.loads(data) # Load recieved data as accessable Dictionary
            print('Successfully retrieved page', i, 'of', st['page']['totalPages'])
        except:
            st = None
            print('=================Retrieving Error=================')

        for ch in st['characters']: # Accessing all recieved characters and append them to all
            all.append(ch)

        if st['page']['lastPage'] == True or i == 3:
            last = True
            continue
        else: i+=1

        time.sleep(2) # Delay to slow down API requests
    return all


def filterStapiCharData(st_data):

    conn = sqlite3.connect('Characters.sqlite')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS ST_Chars (
        id  INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        name    TEXT UNIQUE
    );''')




def load_usa_names(path, firstfilename):

    conn = sqlite3.connect('BD_Project.sqlite')
    cur = conn.cursor()

    filename = re.findall('[a-z]+', firstfilename)[0]
    fileyear = int(re.findall('[0-9]+', firstfilename)[0])

    cur.execute('''
        CREATE TABLE IF NOT EXISTS USA_Names(
            year INT,
            name VARCHAR(20),
            gender VARCHAR(6),
            count INT)
        ''')

    while fileyear <= datetime.datetime.now().year:
        try:
            with open(path + filename + str(fileyear) +".txt") as fh:
                    for line in fh: # Go though file line by line (e.g. Mary,F,7065)
                        ls = line.split(",")

                        n_year = fileyear
                        n_name = ls[0]
                        n_gender = ls[1]
                        n_count = ls[2]

                        if n_gender == 'F': n_gender = 'Female'
                        else:
                            if n_gender == 'M': n_gender = 'Male'
                            else: n_gender = None

                        cur.execute('''INSERT OR IGNORE INTO USA_Names
                            (year, name, gender, count)
                            VALUES ( ?, ?, ?, ?)''',
                            ( n_year, n_name, n_gender, n_count) )
            conn.commit()
            fileyear += 1
        except FileNotFoundError:
            break


f_path = 'D:\\Drive\\OTH\\Big Data Analytics\\Projekt\\Namen\\USA\\'
f_name = 'yob1880'

load_usa_names(f_path, f_name)

# raw_data = getStapiCharData()
# filterStapiCharData(raw_data)
