import sqlite3
import pandas as pd
import re
import datetime
import multiprocessing
from threading import Thread
from joblib import Parallel, delayed
import os
import math
import numpy as np
import requests
import progressbar


def read_txt(path, name):
    year = int(re.findall('[0-9]+', name)[0])
    data = list()
    with open(path + name) as fh:
        for line in fh:
            entry = line.split(",")
            if len(entry) == 3:
                entry.append(year)
                data.append(entry)
            else:
                continue
    return pd.DataFrame(data, columns = ['Name' , 'Gender', 'Count', 'Year'])

def gen_usa_sql_data(df, n=True):
    cmds = list()

    for i in range(df.index.start, (df.index.start+df.shape[0])):
        dic=dict()
        nameid = df.at[i, 'Name']+df.at[i, 'Gender']
        if n == True:
            dic['command'] = 'INSERT OR IGNORE INTO Names(nameid, name, gender) VALUES ( ?, ?, ?);'
            dic['nameid'] = nameid
            dic['actname'] = df.at[i, 'Name']
            dic['gender'] = df.at[i, 'Gender']
        else:
            dic['command'] = 'INSERT OR IGNORE INTO Year_Data(nameid, counts, year) VALUES ( ?, ?, ?);'
            dic['nameid'] = nameid
            dic['year'] = int(df.at[i, 'Year'])
            dic['counts'] = int(df.at[i, 'Count'])
        cmds.append(dic.copy())
    return cmds

def load_usa_names(path, filename):
    print("Loading Dataset USA-Names")

    name = re.findall('[a-z]+', filename)[0]
    year = int(re.findall('[0-9]+', filename)[0])

    filenames = list()
    while year <= datetime.datetime.now().year:
        fname = name+str(year)+".txt"
        if os.path.isfile(path+fname):
            filenames.append(fname)
        year+=1

    core_count = os.cpu_count()
    max_jobs = core_count - 1

    print("\nReading Data")
    name_dfs = Parallel(n_jobs=max_jobs)(delayed(read_txt)(path, name) for name in progressbar.progressbar(filenames))
    del filenames
    print("\nCreating instructions (1/2)") #2 Sequentielle Anweisungen, da doppelte Rückgabe 'too many Values to unpack' wirft. idkw. Vielleicht joblib bug.
    cmds_ls_n = Parallel(n_jobs=max_jobs)(delayed(gen_usa_sql_data)(frame) for frame in progressbar.progressbar(name_dfs))
    print("\nCreating instructions (2/2)")
    cmds_ls_y = Parallel(n_jobs=max_jobs)(delayed(gen_usa_sql_data)(frame, False) for frame in progressbar.progressbar(name_dfs))
    del name_dfs

    print("\nMerging instructions")
    cmds_n = list()
    for commands in progressbar.progressbar(cmds_ls_n):
        for command in commands:
            cmds_n.append(command.copy())
    del cmds_ls_n

    cmds_y = list()
    for commands in progressbar.progressbar(cmds_ls_y):
        for command in commands:
            cmds_y.append(command.copy())
    del cmds_ls_y

    print("\nFilling Database with Names")

    with sqlite3.connect('BD_Project.sqlite') as conn:
        cur = conn.cursor()
        for cmd in progressbar.progressbar(cmds_n):
            cur.execute(cmd['command'], (cmd.get('nameid'), cmd.get('actname'), cmd.get('gender')))
        del cmds_n
        conn.commit()
        print("\nFilling Database with yearly information")
        for cmd in progressbar.progressbar(cmds_y):
            cur.execute(cmd['command'], (cmd.get('nameid'), cmd.get('counts'), cmd.get('year')))
        del cmds_y
        conn.commit()
    print("\nSuccessfully imported dataset USA_Names\n\n\n\n")

def read_tsv(i_path, i_name, column, seperator, encod=None):
    if seperator == "tab":
        seperator = "\t"
    df = pd.read_csv((i_path+i_name), sep=seperator, usecols=column, encoding=encod)
    return df

def gen_imdb_sql_data(df, mode=None):
    i = df.index.start
    cmds = list()
    while i < (df.index.start+df.shape[0]):
        if df.at[i, 'knownForTitles'].split(",")[0] != "\\N":
            dic = dict()
            if mode == None:
                exit()
            elif mode == 'Actors':
                dic['command'] = 'INSERT OR IGNORE INTO Actors(actid, actname) VALUES ( ?, ?);'
                dic['actid'] = df.at[i, 'nconst']
                dic['actname'] = df.at[i, 'primaryName']
                cmds.append(dic.copy())
            elif mode == 'Movies' or mode == 'Cast':
                for id in (df.at[i, 'knownForTitles'].split(",")):
                    if mode == 'Movies':
                        dic['command'] = 'INSERT OR IGNORE INTO Movies(movid) VALUES ( ?);'
                        dic['movid'] = id.strip(",.- ")
                        cmds.append(dic.copy())
                    elif mode == 'Cast':
                        dic['command'] = 'INSERT OR IGNORE INTO Cast(movid, actid) VALUES ( ?, ?);'
                        dic['movid'] = id.strip(",.- ")
                        dic['actid'] = df.at[i, 'nconst']
                        cmds.append(dic.copy())
            else:
                print("Failed in gen_imdb_sql_data, File: Get_Data.py")
                exit()
        i+=1
    return cmds

def load_imdb_register(i_path, i_name):
    print("\n\n\n\nLoading Dataset ImdB_Names")
    core_count = os.cpu_count()
    max_jobs = core_count - 1
    if core_count <=2:
        df = read_tsv(i_path, i_name, ["nconst", "primaryName", "knownForTitles"], "tab")
    else:
        p = multiprocessing.Pool()
        try:
            print("\nReading Data")
            with progressbar.ProgressBar(widgets=[progressbar.Bar()],max_value=6,) as bar:
                res1 = p.apply_async(read_tsv, (i_path, i_name, ["nconst"], "tab"))
                bar.update(int(1), force=True)
                res2 = p.apply_async(read_tsv, (i_path, i_name, ["primaryName"], "tab"))
                bar.update(int(2), force=True)
                res3 = p.apply_async(read_tsv, (i_path, i_name, ["knownForTitles"], "tab"))
                bar.update(int(3), force=True)
                df1 = res1.get()
                bar.update(int(4), force=True)
                df2 = res2.get()
                bar.update(int(5), force=True)
                df3 = res3.get()
                bar.update(int(6), force=True)
            df = df1.join(df2)
            df = df.join(df3)
            del df1, df2, df3
        except:
            print("Failed to read tsv into pandas dataframe")
            exit()

    print("\nCreating instructions and filling Database\n\n\n\n")
    instr = ['Movies', 'Actors', 'Cast']
    for a in range(0, (len(instr))):
        print("Creating instructions ("+str(a+1)+"/3)\n")
        if core_count > 2:
            corecount2 = core_count*core_count
            data_frames = np.array_split(df, corecount2)
            instr_mode = instr[a]
            cmds_ls = Parallel(n_jobs=max_jobs)(delayed(gen_imdb_sql_data)(frame, instr_mode) for frame in progressbar.progressbar(data_frames))
            del data_frames
            print("\nMerging instructions ("+str(a+1)+"/3)\n")
            cmds = list()
            for commands in progressbar.progressbar(cmds_ls):
                for command in commands:
                    cmds.append(command.copy())
            del cmds_ls
        else:
            cmds = gen_imdb_sql_data(df)

        print("\nFilling Database ("+str(a+1)+"/3)\n")
        with sqlite3.connect('BD_Project.sqlite') as conn:
            cur = conn.cursor()
            for cmd in progressbar.progressbar(cmds):
                if cmd.get('actname') != None: #Wenn Command für Actors ist
                    cur.execute(cmd['command'], (cmd['actid'], cmd['actname']))
                elif cmd.get('actid') == None: #Wenn Command für Movies ist
                    cur.execute(cmd['command'], (cmd['movid'],))
                else:
                    cur.execute(cmd['command'], (cmd['movid'], cmd['actid']))
            conn.commit()
        del cmds
    print("\nSuccessfully imported dataset ImdB_Names\n\n\n\n")

def interact_with_db():
    with sqlite3.connect('BD_Project.sqlite') as conn:
        cur = conn.cursor()
        while 1:
            command = input("Input SQL Command:\nPress x for exit\n")
            if command == "":
                continue
            else:
                if command.startswith("SELECT"):
                    try:
                        cur.execute(command)
                        x=cur.fetchall()
                    except:
                        print("Try again.")
                        continue
                    i=0
                    while i<len(x):
                        print(x[i])
                        i+=1
                elif command == "x":
                    break
                else:
                    cur.execute(command)
                    conn.commit()

if __name__ == '__main__':

    usa_path = os.path.abspath("data/Names_USA") + "\\"
    usa_name = 'yob1880.txt'

    i_path = os.path.abspath("data/Names_ImdB") + "\\"
    i_name = 'data.tsv'

    load_usa_names(usa_path, usa_name)
    load_imdb_register(i_path, i_name)
    interact_with_db()
