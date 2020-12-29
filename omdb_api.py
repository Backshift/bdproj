import urllib.request, urllib.parse, urllib.error
import json
import ssl
import math
import datetime
import sqlite3
import time

apiurl = 'http://www.omdbapi.com/?apikey=615a386c&'

def get_search_type():
    parms = dict()
    inp = input("Choose by what you've got:\n  i - IMDb ID\n  t - Exact title\n  s - approximate title(general search)\n").strip(",.- ")
    while 1:
        if inp == "i" or inp == "I":
            parms['i']=input("Enter your IMDb ID:\n").strip(",.- ")
            break
        if inp == "t" or inp == "T":
            parms['t']=input("Enter the exact title:\n").strip(",.- ")
            break
        elif inp == "s" or inp == "S":
            parms['s']=input("Enter your title to search for:\n").strip(",.- ")
            break
        else:
            inp = try_again()

    if parms.get('s')!= None:
        inp = input("Choose:\n  s - series\n  m - movie\n").strip(",.- ")
        while 1:
            if inp == "s" or inp == "S":
                parms['type']="series"
                break
            elif inp == "m" or inp == "M":
                parms['type']="movie"
                break
            else:
                inp = try_again()

        inp = str(input("Year of release, Format like 1974:\n(Enter  n  for no year)\n")).strip(",.- ")
        while 1:
            if inp == "n" or inp == "N":
                break
            try:
                inp = int(inp)
            except:
                inp = try_again()
                continue

            if (inp <= datetime.datetime.now().year) and (inp > 0):
                parms['y'] = inp
                break
            else:
                inp = try_again()


    if (parms.get('i')!= None) or (parms.get('t')!= None):
        parms['plot']='full'

    if parms.get('s')!= None:
        parms['page']= 1

    return parms



def get_api_data(parms):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = apiurl + urllib.parse.urlencode(parms)

    print("Retrieving...\n")
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()

    try:
        js = json.loads(data)
        if js.get('Response') == "True":
            js['Response'] = True
        return js
    except:
        js = dict
        print("Failed to retrieve Information. See below.")
        print(data, "\n")
        return js



def display_api_data(js,parms):
    if (parms.get('s')!= None) and (js.get('Response') == True):
        display_page(js, parms)
        i=0
        while i<len(js['Search']):
            print(str(i+1) + ")")
            print("Title:", js['Search'][i]["Title"])
            print("Year:", js['Search'][i]["Year"])
            print("imdbID:", js['Search'][i]["imdbID"])
            print("Type:", js['Search'][i]["Type"])
            #print("Poster:", js['Search'][i]["Poster"])
            print("\n")
            i+=1
        return True
    elif ((parms.get('i')!= None) or (parms.get('t')!= None)) and (js.get('Response') == True):
        print("Title:", js["Title"])
        print("Year:", js["Year"])
        print("Rated:", js["Rated"])
        print("Rotten Tomatoes:", get_rotten_tomatoes(js))
        print("Released:", js["Released"])
        print("Runtime:", js["Runtime"])
        print("Genre:", js["Genre"])
        print("Director:", js["Director"])
        print("Actors:", js["Actors"])
        print("Plot:", js["Plot"])
        print("Language:", js["Language"])
        print("Country:", js["Country"])
        print("Awards:", js["Awards"])
        #print("Poster:", js["Poster"])
        print("imdbID:", js["imdbID"])
        print("Type:", js["Type"])
        return True
    else:
        print("\nIncorrect Data recieved.\n")
        print(js)
        print("\nExiting...")
        return False


def nav_api_search(js, parms):
    display_page(js, parms)
    current_page, total_pages = get_pages(js, parms)

    inp = input("Enter:\n  n - Next page\n  p - Previous page\n  g - Go to custom page number\n  c - Choose item\n").strip(",.- ")

    while 1:
        if inp == "n" or inp == "N":
            if current_page < total_pages:
                parms['page'] +=1
                break
            else:
                inp = try_again("On last page already.")
                continue

        elif inp == "p" or inp == "P":
            if current_page > 1:
                parms['page'] -= 1
                break
            else:
                inp = try_again("On first page already.")
                continue

        elif inp == "g" or inp == "G":
            display_page(js, parms)
            inp = input("Enter the page you would like to go to. (1,2,3,...)\n").strip(",. ")
            while 1:
                try:
                    inp = int(inp)
                except:
                    inp = try_again("Numbers only.")
                    continue
                if inp >= 1 and inp <= total_pages:
                    parms['page']= inp
                    break
                else:
                    inp = try_again()
                    continue
            break


        elif inp == "c" or inp == "C":
            inp = input("Which of the affore printed items? (1,2,3,...)\n").strip(",. ")
            while 1:
                try:
                    inp = int(inp)
                except:
                    inp = try_again("Numbers only.")
                    continue
                if inp > 0 and inp <= len(js['Search']):
                    parms = dict()
                    parms['i']=js['Search'][inp-1]['imdbID']
                    parms['plot']='full'
                    break
                else:
                    inp = try_again()
                    continue
            break

        else:
            inp = try_again()
            continue

    return parms

def try_again(warning=None):
    if warning != None:
        warning += " Try again.\n"
    else: warning = "Try again.\n"

    return input(warning).strip(",. ")

def get_rotten_tomatoes(js):
    i=0
    if len(js['Ratings']) > 0:
        for rating in js['Ratings']:
            if rating['Source'] == "Rotten Tomatoes":
                return rating['Value']
    else: return None

def display_page(js, parms):
    current_page, total_pages = get_pages(js, parms)
    print("You are at page", current_page, "of", total_pages)

def get_pages(js, parms):
    if parms.get('page') != None:
        current_page = parms['page']
    else: current_page = -1

    if js.get('totalResults') != None:
        total_pages = math.ceil(float(js['totalResults'])/10.0)
    else: total_pages = -1

    return current_page, total_pages

def prompt_save_title(js, parms, parms_old):
    prompt = ("Would you like to save the cast of this " + js["Type"] + " to the database?\nEnter:\n  y - yes\n  n - no\n")
    inp = input(prompt).strip(",. ")
    while 1:
        if inp == "y" or inp == "Y":
            write_to_db(js['Actors'], js['imdbID'])
            break
        elif inp == "n" or inp == "N":
            break
        else:
            inp = try_again()
            continue
    if parms_old.get('s') != None:
        inp = input("Enter:\n  b - back to old search\n  c - create new search\n")
        while 1:
            if inp == "b" or inp == "B":
                return parms_old
            elif inp == "c" or inp == "C":
                return dict()
            else:
                inp = try_again()
    else: return dict()

def write_to_db(names, movie_ID):

    conn = sqlite3.connect('BD_Project.sqlite')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Selected_Actors(
            name VARCHAR(20), --Actors Name
            movie_ID VARCHAR(20), --imdbID
            UNIQUE(name, movie_ID)) --Unique identifier to avoid duplicates
        ''')

    names = names.split(",")
    for name in names:
        cur.execute('''INSERT OR IGNORE INTO Selected_Actors
            (name, movie_ID)
            VALUES ( ?, ?)''',
            (name.strip(",. "), movie_ID) )
        conn.commit()

def prompt_enter_episode(js, parms):
    inp = input("Would you like to enter a specific episode of this series?\n  y - yes\n  n - no\n").strip(",.- ")
    while 1:
        if inp == "y" or inp == "Y":
            inp = input("Which specific season is this episode in?\n").strip(",.- ")
            while 1:
                try:
                    inp = int(inp)
                except:
                    inp = try_again("Enter numbers only.")
                    continue
                if inp >=1 and inp <= int(js.get('totalSeasons')):
                    parms['Season'] = inp
                    print("Parms nach Seasonaddon", parms)
                    break
                else:
                    inp = try_again()
            js = get_api_data(parms)
            if js.get('Response') == True:
                prompt = "Which episode of season " + str(parms['Season']) + " would you like to access?\n"
                inp = input(prompt)
                while 1:
                    try:
                        inp = int(inp)
                    except:
                        inp = try_again("Enter numbers only.")
                        continue
                    if inp >=1 and inp <= len(js.get('Episodes')):
                        print("Episoden", str(len(js.get('Episodes')))) '''XXXXXXXXXXXXXXXXXXXXXXXXXXXHier stimmt was nicht. Nicht genug episoden bzw len gibt 17 statt 21XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'''
                        parms['Episode'] = inp

                        return parms
                        print("Parms nach return?", parms)
                    else:
                        inp = try_again()
            else:
                print("Failed to retrieve. Try again")
                continue
            break

        elif inp == "n" or inp == "N":
            return parms
        else:
            inp = try_again()
            continue

'''XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'''

nav_flag = False
parms_old = dict()
parms = dict()
js = dict()
js['Response'] = True
while 1:
    if (((parms == dict()) or (parms.get('i') != None) or (parms.get('t') != None)) and js.get('Response') == True):
        parms_old = parms
        parms = get_search_type()

    print("Sleeping")
    time.sleep(2)
    js_old = js
    js = get_api_data(parms)

    check = display_api_data(js,parms)
    if check != True:
        parms = dict()
        js['Response'] = True
        continue

    if (parms.get('s') != None) and (js.get('Response') == True):
        parms_old = parms
        parms = nav_api_search(js,parms)
        js = dict()
        continue

    if ((parms.get('i') != None) or (parms.get('t') != None)) and (js.get('Type') == "series") and (js.get('Response') == True):
        parms_old = parms
        print("Parms_old", parms_old)
        print("Parms", parms)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        parms = prompt_enter_episode(js,parms) '''XXXXXXXXXXXDer Dreck ändert einfach parms_old. Ich fasse parms_old nicht mal in der Funktion selbst anXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'''
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("Parms_old", parms_old)
        print("Parms", parms)

        if parms != parms_old:
            js = dict()
            continue

    if (((parms.get('i') != None) or (parms.get('t') != None)) and (js.get('Response') == True)):
        if js_old.get('Type') == 'series' and js.get('Type') == 'episode' and parms == parms_old:
            js['imdbID'] = js_old.get('imdbID')
        parms = prompt_save_title(js,parms,parms_old)
        if parms == parms_old:
            js = dict()
            js['Response'] = True










    '''if parms = parms_old:
            if parms.get('s') != None:
                continue
    else:
        continue'''


    '''parms_old = parms
    if (parms.get('s') != None) and (js.get('Response') == True):
        parms = nav_api_search(js,parms)
    else:
        parms = get_search_type()
    while 1:
        js = get_api_data(parms)
        if js == None:
            break

        check = display_api_data(js,parms)
        if check != True:
            break

        if ((parms.get('i')!= None) or (parms.get('t') != None)) and (js.get('Response') == True):
            parms = prompt_save_title(js,parms,parms_old)
            if parms == parms_old:
                js = get_api_data(parms)
                if js == None:
                    break

                check = display_api_data(js,parms)
                if check != True:
                    break
            break'''
