import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pandas as pd
import os
import numpy as np

par_path = os.path.dirname(os.path.realpath(__file__))

sql_path = par_path + "\\data\\BD_Project.sqlite"

def get_selected_names(sel=False): #Sel=True: get selected data from db; Sel=False: Generate general overview
    with sqlite3.connect(sql_path) as conn:
        cur = conn.cursor()

        cur.execute('''SELECT min(year)
                        FROM Year_Data''')
        result = cur.fetchall()
        min_year = result[0][0]

        if sel:
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

        else:
            filtered_names = ['LukeM', 'ChristianM', 'WolfgangM', 'KurtM', 'PhilippM', 'GloriaF', 'LindaF', 'PaulM', 'BarbaraF', 'CarolineF', 'SandraF', 'MarcusM']

        namedata = dict() #Hirarchy: dict(namedata) -> list of tuples [(1992, 2384, F), (1992, 13, M), ...]
        namedata['Name'] = list()
        namedata['Jahr'] = list()
        namedata['Anzahl'] = list()

        for nameid in filtered_names:
            cur.execute('''SELECT year, counts
                            FROM Year_Data
                            INNER JOIN Names ON Year_Data.nameid = Names.nameid
                            WHERE Names.nameid = ?
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

def print_graphics(df=None, sel=False):

    fig = px.line(
            data_frame=df,
            x='Jahr',
            y='Anzahl',
            #log_y=True,
            title='Namensgebungsrate nach fiktionalen Charakteren in den USA',
            hover_data=['Name', 'Anzahl'],
            color="Name"
    )

    fig.update_traces(mode="lines", hovertemplate=None)

    if sel:
        '''
        fig.add_vrect(x0=1977, x1=(datetime.datetime.now().year-1),
                  annotation_text="decline", annotation_position="top",
                  fillcolor="green", opacity=0.25, line_width=0)
        '''
        updatemenu = [{'buttons': [ #Anakin, Arya, Daenerys, Draco, Han, Hermione, Jeanluc, Kylo, Rey, Seve, Tiberius, Tyrion
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
    else:
        updatemenu = [{'buttons': [ #Christian, Gloria, Kurt, Linda, Luke, Paul, Philipp, Wolfgang
                                    {'method': 'update',
                                     'label': 'Alle Namen',
                                     'args': [{'visible': [True, True, True, True, True, True, True, True],
                                                'title': 'Alle Namen'}]
                                    },
                                    {'method': 'update',
                                     'label': 'Dozenten',
                                     'args': [{'visible': [True, False, True, False, True, False, False, True],
                                                'title': 'Dozenten'}]
                                    },
                                    {'method': 'update',
                                     'label': 'Team F',
                                     'args': [{'visible': [False, True, False, True, True, True, True, False],
                                                'title': 'Team F'}]
                                    }],
                        'direction': 'down',
                        'showactive': True}]

    fig.update_layout(
        updatemenus = updatemenu,
        paper_bgcolor = '#050505',
        plot_bgcolor = '#0f0f0f',
        hovermode = 'x',
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
            rangeslider=dict(
                bgcolor = '#0f0f0f',
                visible=True,
                yaxis = dict(
                    rangemode = 'match'
                ),
                thickness = 0.03
            ),
            gridcolor = '#606060',
            gridwidth = 1
        ),
        yaxis=dict(
            gridcolor = '#606060',
            gridwidth = 1
        )
    )

    if sel:
        fig.write_html(par_path+"\\data\\gesamt.html")
    else:
        fig.write_html(par_path+"\\data\\bekannter_als_Luke.html")
    fig.show()



if __name__ == '__main__':
    data = get_selected_names(True)
    print_graphics(data, True)
    data = get_selected_names(False)
    print_graphics(data, False)
