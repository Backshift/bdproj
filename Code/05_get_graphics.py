import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pandas as pd
import os
import numpy as np

par_path = os.path.dirname(os.path.realpath(__file__))

sql_path = par_path + "\\data\\BD_Project.sqlite"


def get_selected_names():
    with sqlite3.connect(sql_path) as conn:
        cur = conn.cursor()

        cur.execute('''SELECT charname, chargender
                        FROM Selected
                        INNER JOIN M_Cast ON Selected.movid = M_Cast.movid AND Selected.actid = M_Cast.actid''')
        characters = cur.fetchall()
        characters.extend([('Tiberius', 'M'), ('Jeanluc', 'M')])
        characters = list(set(characters))
        filtered_names = list()

        for character in characters: #Goal: Finding out the characters gender before asking the db for non existing values
            charname = character[0].split(" ")[0]
            try:
                chargender = character[1]
                charid = charname+chargender
            except:
                print("Gender for", character, "not set. Please set it manually within the Datbase.")
                chargender = None

            if "-" in charname:
                charname = charname.replace("-", "")

            if chargender == None:
                cur.execute('''SELECT nameid
                                FROM Names
                                WHERE name = ?''', (charname,))
            else:
                cur.execute('''SELECT nameid
                                FROM Names
                                WHERE nameid = ?''', (charid,))
            result = cur.fetchall()

            if len(result) == 0: #Skip, when no Baby was named after the character
                continue
            elif len(result) == 1:
                nameid = [result[0][0]]
            elif len(result) >= 2:
                nameid = list()
                for res in result:
                    nameid.append(res[0])

            filtered_names.extend(nameid)

        filtered_names = list(set(filtered_names))

    updatemenu = [{'buttons': [ #Anakin, Arya, Daenerys, Draco, Han, Hermione, Jeanluc, Kylo, Leia, Luke, Rey, Seven, Tiberius, Tyrion
                                {'method': 'update',
                                 'label': 'Alle Namen',
                                 'args': [{'visible': [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True],
                                            'title': 'Alle Namen'}]
                                },
                                {'method': 'update',
                                 'label': 'Star Trek',
                                 'args': [{'visible': [False, False, False, False, False, False, True, False, False, False, False, True, False, True, False],
                                            'title': 'Star Trek'}]
                                },
                                {'method': 'update',
                                 'label': 'Harry Potter',
                                 'args': [{'visible': [False, False, False, True, False, True, False, False, False, False, False, False, True, False, False],
                                            'title': 'Harry Potter'}]
                                },
                                {'method': 'update',
                                 'label': 'Game of Thrones',
                                 'args': [{'visible': [False, True, True, False, False, False, False, False, False, False, False, False, False, False, True],
                                            'title': 'Game of Thrones'}]
                                },
                                {'method': 'update',
                                 'label': 'Star Wars',
                                 'args': [{'visible': [True, False, False, False, True, False, False, True, True, True, True, False, False, False, False],
                                            'title': 'Game of Thrones'}]
                                }],
                    'direction': 'down',
                    'showactive': True}]

    return filtered_names, updatemenu


def get_class_names():

    names =  ['BarbaraF', 'ChristianM', 'DanielM', 'DennisM', 'EmilM', 'FlorianM', 'GloriaF', 'KarolinF', 'KurtM', 'LindaF', 'LukeM', 'MarcM', 'MarkusM', 'MatthiasM', 'PatriciaF', 'PaulM', 'PhilippM', 'SandraF', 'SergejM', 'TimoM', 'TobiasM', 'WolfgangM']

    updatemenu = [{'buttons': [
                                {'method': 'update',
                                 'label': 'Alle Namen',
                                 'args': [{'visible': [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True],
                                            'title': 'Alle Namen'}]
                                },
                                {'method': 'update',
                                 'label': 'Dozenten',
                                 'args': [{'visible': [False, True, False, False, False, False, False, False, True, False, True, False, False, False, False, False, False, False, False, False, False, True],
                                            'title': 'Dozenten'}]
                                },
                                {'method': 'update',
                                 'label': 'Team F',
                                 'args': [{'visible': [False, False, False, False, False, False, True, False, False, True, True, False, False, False, False, True, True, False, False, False, False, False],
                                            'title': 'Team F'}]
                                }],
                    'direction': 'down',
                    'showactive': True}]

    return names, updatemenu


def to_df(filtered_names):
    with sqlite3.connect(sql_path) as conn:
        cur = conn.cursor()

        cur.execute('''SELECT min(year)
                        FROM Year_Data''')
        result = cur.fetchall()
        min_year = result[0][0]

        namedata = dict() #Hirarchy: dict(namedata) -> list of tuples [(1992, 2384, F), (1992, 13, M), ...]
        namedata['Name'] = list()
        namedata['Jahr'] = list()
        namedata['Anzahl'] = list()

        for nameid in filtered_names:
            cur.execute('''SELECT year, counts
                            FROM Year_Data
                            WHERE nameid = ?
                            ORDER BY year;''', (nameid,))
            result = sorted(cur.fetchall())

            years = list()
            for res in result:
                years.append(res[0])

            for i in range(min_year, datetime.datetime.now().year-1):
                if i in years:
                    namedata['Anzahl'].append(result[years.index(i)][1])
                else:
                    namedata['Anzahl'].append(0)

                namedata['Name'].append(nameid[:-1])
                namedata['Jahr'].append(i)

    df = pd.DataFrame(data=namedata, columns=('Name', 'Jahr', 'Anzahl'))
    #df.replace(0, np.nan, inplace=True)
    df = df.sort_values(by=['Name', 'Jahr'])

    return df

def gen_fig(df, type=""):
    if type == 'trace':
        fig = px.line(
                data_frame=df,
                x='Jahr',
                y='Anzahl',
                #log_y=True,
                hover_data=['Name', 'Anzahl'],
                color='Name'
        )

        fig.update_traces(mode="lines", hovertemplate=None)

    elif type == 'vbar':
        fig=px.bar(
                data_frame=df,
                x='Jahr',
                y='Anzahl',
                color='Name'
        )

        fig.update_layout(barmode='group')
        fig.update_traces(hovertemplate='%{y}')

    return fig

def print_trace_graphics(fig, markers=list(), range=dict(), title="", slider=False, filename="default", updatemenu=None, mode="trace"):
    fig.update_layout(
        updatemenus = updatemenu,
        paper_bgcolor = '#050505',
        plot_bgcolor = '#0f0f0f',
        font = dict(
            color = '#606060',
            family = 'Balto',
            size = 17
        ),
        hoverlabel = dict(
            bgcolor = '#0f0f0f',
            bordercolor = '#606060',
            font = dict(
            size = 12
            )
        ),
        xaxis=dict(
            gridcolor = '#606060',
            gridwidth = 1
        ),
        yaxis=dict(
            gridcolor = '#606060',
            gridwidth = 1
        ),
        dragmode = 'pan'
    )

    if mode == 'trace':
        fig.update_layout(
            hovermode = 'x',
            xaxis=dict(
                range = [range.get('low', min(fig.data[0].x)), range.get('high', max(fig.data[0].x))]
        ))
    elif mode == 'vbar':
        fig.update_layout(
            xaxis=dict(
                range = [range.get('low', min(fig.data[0].x))-0.5, range.get('high', max(fig.data[0].x))+0.5]
        ))


    if title != "":
        fig.update_layout(title=title)

    if slider:
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    bgcolor = '#5f5f5f',
                    visible=True,
                    yaxis = dict(
                        rangemode = 'match'
                    ),
                    thickness = 0.03
                )
        ))

    for marker in markers:
        fig.add_vline(x=marker, line_width=3, line_color="red", opacity = 0.6)

    fig.write_html(par_path+"\\data\\"+filename+".html")
    fig.show()



if __name__ == '__main__':
    names, updatemenu = get_selected_names()
    df = to_df(names)
    fig = gen_fig(df, type='trace')
    print_trace_graphics(fig, title='Namensgebung nach fiktionalen Charakteren in den USA', updatemenu=updatemenu, filename='00_Movienames_gesamt')

    names, updatemenu = get_class_names()
    df = to_df(names)
    fig = gen_fig(df, type='trace')
    print_trace_graphics(fig, title='Bekannter-als-Luke Chart', updatemenu=updatemenu, filename='01_Bekannter_Als_Luke')


    df = to_df(['LukeM'])
    fig = gen_fig(df, type='trace')
    print_trace_graphics(fig, range=dict(low=1940), markers=[1977], filename="Luke")

    df = to_df(['LeiaF'])
    fig = gen_fig(df, type='trace')
    print_trace_graphics(fig, range=dict(low=1970), markers=[1977, 2016], filename="Leia")

    df = to_df(['AnakinM', 'DracoM', 'HermioneF', 'SeverusM'])
    fig = gen_fig(df, type='trace')
    print_trace_graphics(fig, range=dict(low=1990), filename="AnDrHeSe")

    df = to_df(['AryaF'])
    fig = gen_fig(df, type='trace')
    print_trace_graphics(fig, range=dict(low=2000), markers=[2011], filename='Arya')

    df = to_df(['DaenerysF', 'TyrionM'])
    fig = gen_fig(df, type='trace')
    print_trace_graphics(fig, range=dict(low=2000), markers=[2011], filename='DaenTyr')

    df = to_df(['AnakinM', 'HermioneF'])
    fig = gen_fig(df, type='vbar')
    print_trace_graphics(fig, range=dict(low=2001, high=2006), filename='AnHerBalken', mode='vbar')
