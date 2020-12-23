import urllib.request, urllib.parse, urllib.error
import json
import ssl

apiurl = 'http://www.omdbapi.com/?apikey=615a386c&'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def get_search_type():
    parameters = dict()
    inp = input("Choose by what you've got:\n1: i - IMDb ID\n2: t - Exact title\n3: s - approximate title(general search)\n").strip(",.- ")
    while 1:
        if inp == "i" or inp == "I":
            parameters['i']=input("Enter your IMDb ID:\n").strip(",.- ")
            break
        if inp == "t" or inp == "T":
            parameters['t']=input("Enter the exact title:\n").strip(",.- ")
            break
        elif inp == "s" or inp == "S":
            parameters['s']=input("Enter your title to search for:\n").strip(",.- ")
            break
        else:
            inp = input("Try again").strip(",.- ")

    inp = input("Choose:\n1: s - series\n2: m - movie\n3: e - episode\n").strip(",.- ")
    while 1:
        if inp == "s" or inp == "S":
            parameters['type']="series"
            break
        elif inp == "m" or inp == "M":
            parameters['type']="movie"
            break
        elif inp == "e" or inp == "E":
            parameters['type']="episode"
            break
        else:
            inp = input("Try again").strip(",.- ")

    inp = input("Year of release, Format like 1974:\n(Enter  n  for no year)\n").strip(",.- ")
    if inp != "n" or inp == "N":
        parameters['y']=inp

    if (parameters.get('i',-1)!= -1) or (parameters.get('t',-1)!= -1):
        parameters['plot']='full'

    if parameters.get('s',-1)!= -1:
        parameters['page']= 1

    return parameters



def get_api_data(parms):
    url = apiurl + urllib.parse.urlencode(parms)

    print('Retrieving', url)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()

    try:
        js = json.loads(data)
    except:
        js = None

    if parms.get('s', -1)!= -1:
        i=0
        while i<len(js['Search']):
            print(js['Search'][i])
            i+=1
    print("\n\n\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print(data)
#    elif (parameters.get('i',-1)!= -1) or (parameters.get('t',-1)!= -1):



parameters = get_search_type()
get_api_data(parameters)
