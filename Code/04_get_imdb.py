import requests
import sqlite3
import json
import time
import os
import progressbar

par_path = os.path.dirname(os.path.realpath(__file__))
sql_path = par_path + "\\data\\BD_Project.sqlite"



def compl_sel_data():
    with sqlite3.connect(sql_path) as conn:
        cur = conn.cursor()

        cur.execute('''SELECT movid,actid,actname
                        FROM Selected''')
        selected = cur.fetchall() #Format: [('tt0060028', None, 'Leonard Nimoy'), ('tt0060028', None, 'William Shatner')]

        res_ids = list() #Format: [[Patrick Stewart, tt0060028, nm0001772, nm9999492, nm0000434], [Leonard Nimoy, tt0060028, nm0001772, nm9999492, nm0000434]]
        for t_selected in selected: #Collecting ids - For every tuple ('tt0060028', 'nm9999492', 'Leonard Nimoy')
            if t_selected[1] == None or not t_selected[1].startswith('nm'):
                cur.execute('''SELECT actid, actname
                                FROM Actors
                                WHERE actname = ?''', (t_selected[2],))
                known_acts = cur.fetchall().sort()
                entry = list() #Format: [Patrick Stewart, tt0060028, nm0001772, nm9999492, nm0000434]
                entry.extend([known_acts[0][1],t_selected[0]])

                if len(known_acts) == 1:
                    cur.execute('''INSERT INTO Selected
                                    (movid, actid, actname)
                                    VALUES ( ?, ?, ?) ON CONFLICT (movid, actname) DO UPDATE SET actid = ?''',
                                    (t_selected[0], known_acts[0][0], known_acts[0][1], known_acts[0][0]))
                    conn.commit()

                for known_act in known_acts: #Format: (nm0001772; Patrick Stewart)
                    print(known_act[0])
                    entry.append(known_act[0])
                print("\n\n\n")

            else:
                entry = [t_selected[2], t_selected[0], t_selected[1]]

            res_ids.append(entry)

        res_ids4api = list() #Set for ids, that will be sent to the api to collect additional data

        for actor in res_ids:
            ids = set()
            for i in range(2, len(actor)):
                cur.execute('''SELECT M_Cast.actid AS actid, actname, movid, M_Cast.charname
                                FROM M_Cast
                                INNER JOIN Actors ON M_Cast.actid=Actors.actid
                                WHERE M_Cast.actid = ? AND movid = ?''', (actor[i], actor[1]))
                cast_result = cur.fetchall()

                if len(cast_result) == 1: #If 1 actid/movid pair was found ("Has that actor worked in this specific movie?")
                    if cast_result[0][3] == None or cast_result[0][3] == "": #That actor worked on the movie, but we've got no character name
                        ids = set()
                        ids.add(actor[i])
                    cur.execute('''INSERT INTO Selected
                                    (movid, actid, actname) VALUES ( ?, ?, ?)
                                    ON CONFLICT (movid, actname) DO UPDATE SET actid = ?''',
                                    (cast_result[0][2], actor[i], cast_result[0][1], actor[i]))
                    conn.commit()
                    break

                elif len(cast_result) == 0: #If no actor/movie pair was found
                    ids.add(actor[i])

                elif len(cast_result) > 1:
                    print("More than 1 actor with id", actor[i], "played in movie/series with id", cast_result[0][2], "\nPlease delete double entries. Skipping enty.\n")
            res_ids4api.extend(ids)
        return res_ids4api


######################################################################################################################################################



def load_api_data():
    p = par_path + "\\data\\imdb_api_data\\"
    if not os.path.exists(p):
        try:
            os.makedirs(p)
        except OSError:
            print ('Error: Creating directory. ' +  p)

    ids = compl_sel_data()
    ids_old = ids.copy()
    first_length = len(ids)
    with sqlite3.connect(sql_path) as conn:
        cur = conn.cursor()
        i=0
        while len(ids) > 0:
            print("("+str(len(ids))+"/"+str(first_length)+") possible requests remaining.")
            if ids == ids_old:
                i+=1
            else:
                i=0
            act = ids[i]
            p = par_path + "\\data\\imdb_api_data\\" + act + ".txt"

            if os.path.isfile(p):
                print("Opening", act, "from File.")
                with open(p, 'r', encoding='utf-8') as f:
                    js = json.loads(f.read())
            else:
                tries=0
                while tries>-1 and tries<5:
                    if tries>0:
                        print('Retrying', act, 'again because json conversion failed. ('+tries+'/5)')

                    msg = "Retrieving id: " + str(act)
                    if i > 0:
                        msg += "\nActor with same name, Nr." + str(i+1)
                    print(msg)
                    jstext = get_imdb_api_data(act)
                    with open(p, 'w', encoding='utf-8') as f:
                        f.write(jstext)
                    try:
                        js = json.loads(jstext)
                        tries= -1
                    except:
                        tries+=1

            if js['filmography'] != None:
                for mov in js['filmography']:
                    if 'year' in mov and 'characters' in mov:
                        if 'attr' in mov:
                            skip = 0
                            for attr in mov['attr']: #Voice acting is not part of our world here, really
                                if attr == "voice":
                                    skip = 1
                            if skip == 1: #Special breakyboi to continue the big mov/js loop, if voiceacting was found. (clearer Method than comprimised notation)
                                continue
                        movid = mov['id'].split("/") #format: /title/tt8806524/
                        for el in movid:
                            if el.startswith("tt"):
                                movid = el
                                break
                        charname = mov['characters'][0]
                        if charname.startswith("Self ") or charname == 'Self' or charname.startswith('Various') or charname == js['base']['name'] or charname == 'Presenter' or charname == 'Narrator':
                            continue
                        titles = ['Lt.', 'Cmdr.', 'Comm.' 'Commander', 'Colonel', 'Col.', 'Counselor', 'Dr.', 'Doctor', 'Capt.', 'Captain', 'Cap ' 'Adm.', 'Admiral', 'Sgt.', 'Major', 'Maj.', 'Seargant', 'Host', 'Insp.', 'Inspector', 'Chief', 'Senator', 'King', 'Mr.', 'Mister', 'Ms.', 'Ms', 'Miss', 'Mrs.', 'Mrs', 'Misses', 'Prof.', 'Professor', 'Asst.', 'Sir ']
                        i = 0
                        while i >= 0:
                            for prefix in titles:
                                i=charname.find(prefix)
                                charname = charname.replace(prefix, "")
                            if charname == "":
                                break
                        charname = charname.strip()

                        cur.execute('''INSERT INTO M_Cast
                                        (movid, actid, charname) VALUES ( ?, ?, ?)
                                        ON CONFLICT (movid, actid) DO UPDATE SET charname = ?''',
                                        (movid, act, mov['characters'][0], charname))
                        cur.execute('''INSERT INTO Movies
                                        (movid, title, year) VALUES ( ?, ?, ?)
                                        ON CONFLICT (movid) DO UPDATE SET title = ?, year = ?''',
                                        (movid, mov['title'], int(mov['year']), mov['title'], int(mov['year'])))
                conn.commit()
            ids_old = ids.copy()
            ids = compl_sel_data()


def get_imdb_api_data(id):
    time.sleep(0.2)
    url = "https://imdb8.p.rapidapi.com/actors/get-all-filmography"
    headers = {
    'x-rapidapi-key': "cda9398349mshadb0f4bf9936df2p150033jsnfd209e9bab4f",
    'x-rapidapi-host': "imdb8.p.rapidapi.com"}

    querystring = {"nconst": id}
    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text

if __name__ == "__main__":
    load_api_data()
