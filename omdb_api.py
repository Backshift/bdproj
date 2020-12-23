import urllib.request, urllib.parse, urllib.error
import json
import ssl
import math
import datetime

apiurl = 'http://www.omdbapi.com/?apikey=615a386c&'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def get_search_type():
    parms = dict()
    inp = input("Choose by what you've got:\n1: i - IMDb ID\n2: t - Exact title\n3: s - approximate title(general search)\n").strip(",.- ")
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

    if (parms.get('s',None)!= None) or (parms.get('t',None)!= None):
        inp = input("Choose:\n1: s - series\n2: m - movie\n3: e - episode\n").strip(",.- ")
        while 1:
            if inp == "s" or inp == "S":
                parms['type']="series"
                break
            elif inp == "m" or inp == "M":
                parms['type']="movie"
                break
            elif inp == "e" or inp == "E":
                parms['type']="episode"
                break
            else:
                inp = try_again()

    if (parms.get('s',None)!= None) or (parms.get('t',None)!= None):
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


    if (parms.get('i',None)!= None) or (parms.get('t',None)!= None):
        parms['plot']='full'

    if parms.get('s',None)!= None:
        parms['page']= 1

    return parms



def get_api_data(parms):
    url = apiurl + urllib.parse.urlencode(parms)

    print('Retrieving', url, "\n")
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()

    try:
        js = json.loads(data)
        if js['Response'] == "True":
            js['Response'] = True
        return js
    except:
        js = None
        print("Failed to retrieve Information. See below.")
        print(data, "\n")
        return None




def display_api_data(js,parms):
    if (parms.get('s', None)!= None) and (js['Response'] == True):
        i=0
        while i<len(js['Search']):
            print("Title:", js['Search'][i]["Title"])
            print("Year:", js['Search'][i]["Year"])
            print("imdbID:", js['Search'][i]["imdbID"])
            print("Type:", js['Search'][i]["Type"])
            print("Poster:", js['Search'][i]["Poster"])
            print("\n")
            i+=1
        return True
    elif ((parms.get('i',None)!= None) or (parms.get('t',None)!= None)) and (js['Response'] == True):
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
        print("Poster:", js["Poster"])
        print("imdbID:", js["imdbID"])
        print("Type:", js["Type"])
        print("\n")
        return True
    else:
        print("Failed to display. Exiting\n")
        return False


def nav_api_search(js, parms):
    current_page = parms['page']
    total_pages = math.ceil(float(js['totalResults'])/float(len(js['Search'])))
    print("You are at page", current_page, "of", total_pages)
    inp = input("Choose:\n1.  n  Next page\n2.  p  Previous page\n3.  c  Choose item\n").strip(",.- ")

    while 1:
        if inp == "n" or inp == "N":
            if current_page < total_pages:
                parms['page'] +=1
            else:
                try_again()
                continue
            break

        elif inp == "p" or inp == "P":
            if current_page > 1:
                parms['page'] -= 1
            else:
                try_again()
                continue
            break

        elif inp == "c" or inp == "C":
            inp = input("Which of the affore printed items? (1,2,3,...)\n").strip(",.- ")
            while 1:
                try:
                    inp = int(inp)
                except:
                    print("except")
                    inp = try_again()
                    continue
                if inp > 0 and inp <= len(js['Search']):
                    parms = dict()
                    parms['i']=js['Search'][inp-1]['imdbID']
                    return parms
                else:
                    print("else1")
                    inp = try_again()
                    continue
        else:
            print("else2")
            inp = try_again()
            continue
    return parms

def try_again():
    return input("Try again...\n").strip(",.- ")

def get_rotten_tomatoes(js):
    i=0
    if len(js['Ratings']) > 0:
        for rating in js['Ratings']:
            if rating['Source'] == "Rotten Tomatoes":
                return rating['Value']
    else: return None

nav_flag = False
while 1:
    if nav_flag == False:
        parms = get_search_type()
    else:
        if parms.get('s', None)!= None:
            parms = nav_api_search(json_data, parms)


    json_data = get_api_data(parms)
    if json_data == None:
        continue

    check = display_api_data(json_data,parms)
    if check != True:
        continue


    if (parms.get('s', None)!= None) and (json_data['Response'] == True):
        nav_flag = True
    else:
        nav_flag = False
