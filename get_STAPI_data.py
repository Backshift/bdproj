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


    all = list() # List for all recieved STAPI data, for return use
    last=False
    i=0
    parms = dict() # Parameters to give the API (none in this case)

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

    all = str(all)
    fh.write(all) # Write data to logfile
    fh.close()
    print("Success.")
    time.sleep(3)
    print(all)
    print("Data:")
    print(data)

    return all



getStapiCharData('_stapi_files.txt')
