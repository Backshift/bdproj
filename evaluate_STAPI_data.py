import json

fh = open('_stapi_files.txt', 'r')
fh = fh.read()


st = json.loads(fh)

print(st)
