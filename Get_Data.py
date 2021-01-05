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
    return pd.DataFrame(data, columns = ['Name', 'Gender', 'Count', 'Year'])

def gen_usa_sql_data(df):
    cmds = list()
    for i in range(df.index.start, (df.index.start+df.shape[0])):
        dic=dict()
        dic['command'] = 'INSERT OR IGNORE INTO USA_Names (year, name, gender, counts) VALUES ( ?, ?, ?, ?);'
        dic['year'] = int(df.at[i, 'Year'])
        dic['name'] = df.at[i, 'Name']
        dic['gender'] = df.at[i, 'Gender']
        dic['counts'] = int(df.at[i, 'Count'])
        cmds.append(dic)
    return cmds

def load_usa_names(path, filename):
    print("Loading Dataset USA_Names")

    name = re.findall('[a-z]+', filename)[0]
    year = int(re.findall('[0-9]+', filename)[0])

    filenames = list()
    while year <= datetime.datetime.now().year:
        fname = name+str(year)+".txt"
        if os.path.isfile(path+fname):
            filenames.append(fname)
        year+=1
    core_count = os.cpu_count()
    print("\nReading Data")
    name_dfs = Parallel(n_jobs=core_count-1)(delayed(read_txt)(path, name) for name in progressbar.progressbar(filenames))
    print("\nCreating instructions")
    cmds_ls = Parallel(n_jobs=core_count-1)(delayed(gen_usa_sql_data)(frame) for frame in progressbar.progressbar(name_dfs))

    print("\nMerging instructions")
    cmds = list()
    for commands in progressbar.progressbar(cmds_ls):
        for command in commands:
            cmds.append(command)
    del cmds_ls
    print("\nCreating Database")
    con = sqlite3.connect('BD_Project.sqlite')
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS USA_Names(
            year INT, --Year of Birth
            name VARCHAR(20), --Name given
            gender VARCHAR(6), --Gender
            counts INT, --How many that year
            UNIQUE(year, name, gender)) --Unique identifier to avoid duplicates
        ''')
    print("\nFilling Database")
    for cmd in progressbar.progressbar(cmds):
        cur.execute(cmd['command'], (cmd['year'], cmd['name'], cmd['gender'], cmd['counts']))
    con.commit()
    con.close()
    print("\nSuccessfully imported dataset USA_Names")

def read_tsv(i_path, i_name, column, seperator, encod=None):
    if seperator == "tab":
        seperator = "\t"
    df = pd.read_csv((i_path+i_name), sep=seperator, usecols=column, encoding=encod)
    return df

def gen_imdb_sql_data(df):
    i = df.index.start
    cmds = list()
    while i < (df.index.start+df.shape[0]):
        dic=dict()
        dic['command'] = 'INSERT OR IGNORE INTO name_ids (act_id, act_name) VALUES ( ?, ?);'
        dic['act_id'] = df.at[i, 'nconst']
        dic['act_name'] = df.at[i, 'primaryName']
        cmds.append(dic)
        i+=1
    return cmds

def load_imdb_register(i_path, i_name):
    print("\n\n\n\nLoading Dataset ImdB_Names")
    core_count = os.cpu_count()
    if core_count <=2:
        df = read_tsv(i_path, i_name, ["nconst", "primaryName"], "tab")
    else:
        p = multiprocessing.Pool()
        try:
            print("\nReading Data")
            with progressbar.ProgressBar(widgets=[progressbar.Bar()],max_value=4,) as bar:
                res1 = p.apply_async(read_tsv, (i_path, i_name, ["nconst"], "tab"))
                bar.update(int(1), force=True)
                res2 = p.apply_async(read_tsv, (i_path, i_name, ["primaryName"], "tab"))
                bar.update(int(2), force=True)
                df1 = res1.get()
                bar.update(int(3), force=True)
                df2 = res2.get()
                bar.update(int(4), force=True)
            df = df1.join(df2)
            del df1, df2
        except:
            print("Failed to read tsv into pandas dataframe")
            exit()

    print("\nCreating instructions")
    if core_count > 2:
        core_count2 = core_count*core_count
        data_frames = np.array_split(df, core_count2)
        cmds_ls = Parallel(n_jobs=core_count-1)(delayed(gen_imdb_sql_data)(frame) for frame in progressbar.progressbar(data_frames))
        del data_frames
        print("\nMerging instructions")
        cmds = list()
        for commands in progressbar.progressbar(cmds_ls):
            for command in commands:
                cmds.append(command)
        del cmds_ls
    else:
        cmds = gen_imdb_sql_data(df)

    print("\nCreating Database")
    con = sqlite3.connect('BD_Project.sqlite')
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS name_ids(
            act_id VARCHAR(20), --actors imdb id
            act_name VARCHAR(40), --actors name
            UNIQUE(act_id, act_name)); --Unique identifier to avoid duplicates
        ''')
    print("\nFilling Database")
    for cmd in progressbar.progressbar(cmds):
        cur.execute(cmd['command'], (cmd['act_id'], cmd['act_name']))
    con.commit()
    con.close()
    print("\nSuccessfully imported dataset ImdB_Names\n\n\n\n")

def interact_with_db():
    con = sqlite3.connect('BD_Project.sqlite')
    cur = con.cursor()
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
                con.commit()


if __name__ == '__main__':

    usa_path = os.path.abspath("data/Names_USA") + "\\"
    usa_name = 'yob1880.txt'

    i_path = os.path.abspath("data/Names_ImdB") + "\\"
    i_name = 'data.tsv'


    #load_usa_names(usa_path, usa_name)
    load_imdb_register(i_path, i_name)
    interact_with_db()
