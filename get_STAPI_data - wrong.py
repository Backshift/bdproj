import urllib.request, urllib.parse, urllib.error
import json
import ssl
import time

def getStapiCharData(logname):

    serurl = 'http://stapi.co/api/v1/rest/character/search?' # API URL

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Open or create logfile for STAPI data
    fh = open(logname,'w')


    alllist = list() # List for all recieved STAPI data, for return use
    alljson = '{' # String for all recieved STAPI data, for writing use, in JSON format
    last=False
    i=0
    parms = dict() # Parameters to give the API (none in this case)

    while last == False: # Collect data until API states 'lastPage'
        parms['pageNumber'] = i
        url = serurl + urllib.parse.urlencode(parms) + '&pretty' # Encode URL to send to API
        print('Retrieving', url)
        uh = urllib.request.urlopen(url, context=ctx) # Send API request
        data = uh.read().decode() # Decode recieved Data (UTF-8? -> UNICODE)

        begin = False
        for line in data: # Gather JSON Data for later use

            if begin == True:
                alljson += line
                continue

            if line.strip().startswith('"characters" : [ {'):
                alljson += line
                begin = True

        alljon=alljson[:-1]

        try:
            st = json.loads(data) # Load recieved data as accessable Dictionary
            print('Successfully retrieved page', i, 'of', st['page']['totalPages'])
        except:
            st = None
            print('=================Retrieving Error=================')

        for ch in st['characters']: # Accessing all recieved characters and append them to alllist
            alllist.append(ch)

        if st['page']['lastPage'] == True or i == 1:
            last = True
            continue
        else: i+=1

        time.sleep(2) # Delay to slow down API requests

    alljson += "}"
    fh.write(alljson) # Write data to logfile
    fh.close()
    print("Success.")
    time.sleep(3)
    print(alllist)
    print("Data:")
    print(data)

    return alllist



getStapiCharData('_stapi_files.txt')
