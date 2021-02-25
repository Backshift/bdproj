import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pandas as pd
import os
import numpy as np
import math as m

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

        if len(filtered_names)>0:
            filtered_names = list(set(filtered_names))
        else:
            exit()

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
                    'showactive': True,
                    'bordercolor': 'rgba(255,255,255,0.2)'}]

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
                    'showactive': True,
                    'bordercolor': 'rgba(255,255,255,0.2)'}]

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

def gen_fig(df, type="", colours=['#00b7ff', '#e66ee6', '#6A76FC', 'DarkSeaGreen', 'Orange', 'OrangeRed', '#d90000', '#ff4646', '#00b7ff', '#0cbb06', '#ffc800', 'ForestGreen', 'Gray', '#c69e02', 'PaleGoldenRod', '#B68E00', '#C9FBE5', '#FF0092', '#22FFA7', '#E3EE9E', '#86CE00', '#BC7196', '#7E7DCD', '#FC6955', '#E48F72']):
    if type == 'trace':
        fig = px.line(
                data_frame=df,
                x='Jahr',
                y='Anzahl',
                #log_y=True,
                hover_data=['Name', 'Anzahl'],
                line_shape="spline",
                render_mode='svg',
                color='Name',
                color_discrete_sequence=colours
        )

        fig.update_traces(mode="lines", hovertemplate=None, line_width=2)

    elif type == 'vbar':
        fig=px.bar(
                data_frame=df,
                x='Jahr',
                y='Anzahl',
                color='Name',
                color_discrete_sequence=colours
        )

        fig.update_layout(barmode='group')
        fig.update_traces(hovertemplate='%{y}')

    return fig

def print_trace_graphics(fig, markers=list(), range=dict(), title="", slider=False, filename="default", updatemenu=None, mode="trace", height='500px'):
    fig.update_layout(
        updatemenus = updatemenu,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font = dict(
            color = '#dcdcdc',
            family = 'Source Sans Pro',
            size = 16
        ),
        hoverlabel = dict(
            bgcolor = '#000000',
            #bordercolor = 'rgba(0,0,0,0)',
            font = dict(
            size = 12
            )
        ),
        xaxis=dict(
            gridcolor = '#acacac',
            gridwidth = 1
        ),
        yaxis=dict(
            gridcolor = '#acacac',
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
        fig.update_layout( title={
                            'text': title,
                            'y':1,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
                            title_font_size=25)

    if slider:
        if height != '500px':
            thick=0.05
        else:
            thick=0.1

        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    bgcolor = '#101010',
                    visible=True,
                    yaxis = dict(
                        rangemode = 'match'
                    ),
                    thickness = thick
                )
        ))

    for marker in markers:
        fig.add_vline(x=marker, line_width=2, line_color="yellow", opacity = 0.7)

    fig.write_html(file=(par_path+"\\data\\"+filename+".html"), include_plotlyjs='cdn', full_html=False, default_height=height)
    fig.write_html(file=("C:\\xampp\\htdocs\\graphs\\"+filename+".html"), include_plotlyjs='cdn', full_html=False, default_height=height)

################################################################################################################################################################

if __name__ == '__main__':
    names, updatemenu = get_selected_names()
    df = to_df(names)
    fig = gen_fig(df, type='trace')
    print_trace_graphics(fig, title='Namensgebung nach fiktiven Charakteren in den USA', slider=True, updatemenu=updatemenu, filename='00_Movienames_gesamt', height='800px')

    names, updatemenu = get_class_names()
    df = to_df(names)
    fig = gen_fig(df, type='trace', colours=['#ff0000', '#e66ee6', '#6A76FC', 'DarkSeaGreen', '#b300ff', 'OrangeRed', '#d90000', '#ff4646', '#00b7ff', '#ffc800', '#0cbb06', 'ForestGreen', 'Gray', 'Orange', 'PaleGoldenRod', 'Orange', '#C9FBE5', '#FF0092', '#22FFA7', '#E3EE9E', '#86CE00', '#BC7196', '#7E7DCD', '#FC6955', '#E48F72'])
    print_trace_graphics(fig, title='Schlag den Luke', slider=True, updatemenu=updatemenu, filename='01_Bekannter_Als_Luke', height='800px')


    df = to_df(['LukeM'])
    fig = gen_fig(df, type='trace', colours=['#0cbb06'])
    print_trace_graphics(fig, range=dict(low=1940), markers=[1977], filename="Luke")

    df = to_df(['LeiaF'])
    fig = gen_fig(df, type='trace', colours=['#00b7ff'])
    print_trace_graphics(fig, range=dict(low=1970), markers=[1977, 2016], filename="Leia")

    df = to_df(['AnakinM', 'DracoM', 'HermioneF', 'SeverusM'])
    fig = gen_fig(df, type='trace', colours=['#00b7ff', 'DarkSeaGreen', 'OrangeRed', 'Gray'])
    print_trace_graphics(fig, range=dict(low=1990), filename="AnDrHeSe")

    df = to_df(['AryaF'])
    fig = gen_fig(df, type='trace', colours=['#e66ee6'])
    print_trace_graphics(fig, range=dict(low=2000), markers=[2011], filename='Arya')

    df = to_df(['DaenerysF', 'TyrionM'])
    fig = gen_fig(df, type='trace', colours=['#6A76FC', 'PaleGoldenRod'])
    print_trace_graphics(fig, range=dict(low=2000), markers=[2011], filename='DaenTyr')

    df = to_df(['AnakinM', 'HermioneF'])
    fig = gen_fig(df, type='vbar', colours=['#00b7ff', 'OrangeRed'])
    print_trace_graphics(fig, range=dict(low=2001, high=2006), filename='AnHerBalken', mode='vbar')
