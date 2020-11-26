import urllib.request, urllib.parse, urllib.error
import json
import ssl



serviceurl = 'http://www.omdbapi.com/?apikey=615a386c&'

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE



parms = dict()
parms['s'] = input("Filmname eingeben ")
parms['type'] = 'series'

url = serviceurl + urllib.parse.urlencode(parms)

print('Retrieving', url)
uh = urllib.request.urlopen(url, context=ctx)
data = uh.read().decode()

try:
    js = json.loads(data)
except:
    js = None

if not js or 'status' not in js or js['status'] != 'OK':
    print('==== Failure To Retrieve ====')
    print(data)
