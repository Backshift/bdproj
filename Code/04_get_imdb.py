import requests
import sqlite3
import json
import time
import os
import progressbar

par_path = os.path.dirname(os.path.realpath(__file__))
sql_path = par_path + "\\data\\BD_Project.sqlite"



def get_sel_data():
    with sqlite3.connect(sql_path) as conn:
        cur = conn.cursor()

        cur.execute('''SELECT movid,actid,actname
                        FROM Selected''')
        selected = cur.fetchall() #Format: [('tt0060028', None, 'Leonard Nimoy'), ('tt0060028', None, 'William Shatner')]

        res_ids = list() #Format: [[Patrick Stewart, tt0060028, nm0001772, nm9999492, nm0000434], [Leonard Nimoy, tt0060028, nm0001772, nm9999492, nm0000434]]
        print("\nCollecting possible actor-ids")
        for t_selected in selected: #Collecting ids - For every tuple ('tt0060028', 'nm9999492', 'Leonard Nimoy')
            if t_selected[1] == None or not t_selected[1].startswith('nm'):
                cur.execute('''SELECT actid, actname
                                FROM Actors
                                WHERE actname = ?
                                GROUP BY actid''', (t_selected[2],))
                known_acts = cur.fetchall()

                entry = list() #Format: [Patrick Stewart, tt0060028, nm0001772, nm9999492, nm0000434]
                if len(known_acts) == 0:
                    continue

                entry.extend([known_acts[0][1],t_selected[0]]) #Patrick Stewart, tt0060028

                if len(known_acts) == 1:
                    cur.execute('''INSERT INTO Selected
                                    (movid, actid, actname)
                                    VALUES ( ?, ?, ?) ON CONFLICT (movid, actname) DO UPDATE SET actid = ?''',
                                    (t_selected[0], known_acts[0][0], known_acts[0][1], known_acts[0][0]))
                    conn.commit()

                for known_act in known_acts: #Format: (nm0001772; Patrick Stewart)
                    entry.append(known_act[0])

            else:
                entry = [t_selected[2], t_selected[0], t_selected[1]]

            res_ids.append(entry)

        res_ids4api = list() #Set for ids, that will be sent to the api to collect additional data

        for actor in res_ids:
            ids = list()
            for a in range(2, len(actor)):
                cur.execute('''SELECT M_Cast.actid, actname, movid, M_Cast.charname
                                FROM M_Cast
                                INNER JOIN Actors ON M_Cast.actid=Actors.actid
                                WHERE M_Cast.actid = ? AND movid = ?''', (actor[a], actor[1]))
                cast_result = cur.fetchall()

                if len(cast_result) == 1: #If 1 actid/movid pair was found ("Has that actor worked in this specific movie?")
                    if cast_result[0][3] == None or cast_result[0][3] == "": #That actor worked on the movie, but we've got no character name
                        ids = list()
                        ids.append(actor[a])
                    cur.execute('''INSERT INTO Selected
                                    (movid, actid, actname) VALUES ( ?, ?, ?)
                                    ON CONFLICT (movid, actname) DO UPDATE SET actid = ?''',
                                    (cast_result[0][2], actor[a], cast_result[0][1], actor[a]))
                    conn.commit()
                    break

                elif len(cast_result) == 0: #If no actor/movie pair was found
                    if actor[a] not in ids:
                        ids.append(actor[a])

                elif len(cast_result) > 1:
                    print("More than 1 actor with id", actor[a], "played in movie/series with id", cast_result[0][2], "\nPlease delete double entries. Skipping enty.\n")
                    continue
            res_ids4api.extend(sorted(ids)) #Sorted to minimise API calls (lower actids have been found to relate to more popular actors)
        return res_ids4api

def load_api_data():
    p = par_path + "\\data\\imdb_api_data\\"
    if not os.path.exists(p):
        try:
            os.makedirs(p)
        except OSError:
            print ('Error: Creating directory. ' +  p)

    print("Accessing Database...\n")
    ids = get_sel_data()
    ids_old = list()
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

                    print("Retrieving id: " + str(act))
                    jstext = get_imdb_api_data(act,p)
                    try:
                        js = json.loads(jstext)
                        tries= -1
                    except:
                        tries+=1

            if js['filmography'] != None:
                for mov in js['filmography']:
                    if 'year' in mov and 'characters' in mov:

                        if 'attr' in mov:
                            if "voice" in mov['attr']:
                                continue

                        movid = mov['id'].split("/") #format: /title/tt8806524/
                        charname = mov['characters'][0]

                        for el in movid:
                            if el.startswith("tt"):
                                movid = el
                                break

                        titles = ['The', 'Baby', 'Lt.', 'Lieutenant', 'Cmdr.', 'Comm.', 'Commander', 'Commandant', 'Colonel', 'Col.', 'Counselor', 'Dr.', 'Doctor', 'Capt.', 'Princess', 'Prince', 'Lord', 'Captain', 'Cap ' 'Adm.', 'Admiral', 'Sgt.', 'Major', 'Maj.', 'Seargant', 'Host', 'Insp.', 'Inspector', 'Chief', 'Senator', 'King', 'Mr.', 'Mister', 'Ms.', 'Ms', 'Miss', 'Mrs.', 'Mrs', 'Misses', 'Prof.', 'Professor', 'Asst.', 'Sir ']
                        if charname.startswith("Self ") or charname == 'Self' or charname.startswith('Various') or charname == js['base']['name'] or charname == 'Presenter' or charname == 'Narrator':
                            continue

                        for prefix in titles:
                            if prefix in charname:
                                charname = charname.replace(prefix, "")
                        if charname.strip() == "":
                            continue

                        charname_temp = ""
                        for namepart in charname.split():
                            charname_temp += (namepart+" ")
                        charname = charname_temp.strip()

                        cur.execute('''INSERT INTO M_Cast
                                        (movid, actid, charname) VALUES ( ?, ?, ?)
                                        ON CONFLICT (movid, actid) DO UPDATE SET charname = ?''',
                                        (movid, act, charname, charname))
                        cur.execute('''INSERT INTO Movies
                                        (movid, title, year) VALUES ( ?, ?, ?)
                                        ON CONFLICT (movid) DO UPDATE SET title = ?, year = ?''',
                                        (movid, mov['title'], int(mov['year']), mov['title'], int(mov['year'])))
                conn.commit()
            ids_old = ids.copy()
            ids = get_sel_data()

def get_imdb_api_data(id,p):
    time.sleep(0.2)
    url = "https://imdb8.p.rapidapi.com/actors/get-all-filmography"
    headers = {
    'x-rapidapi-key': "cda9398349mshadb0f4bf9936df2p150033jsnfd209e9bab4f",
    'x-rapidapi-host': "imdb8.p.rapidapi.com"}

    querystring = {"nconst": id}
    response = requests.request("GET", url, headers=headers, params=querystring)

    with open(p, 'w', encoding='utf-8') as f:
        f.write(response.text)

    return response.text

if __name__ == "__main__":
    load_api_data()
