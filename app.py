# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import functions as fun
import plotly
import datetime
import calendar
import plotly.graph_objs as go
import numpy as np

from six.moves.urllib.parse import quote

def discrete_colorscale(bvals, colors):
    """
    bvals - list of values bounding intervals/ranges of interest
    colors - list of rgb or hex colorcodes for values in [bvals[k], bvals[k+1]],0<=k < len(bvals)-1
    returns the plotly  discrete colorscale
    """
    if len(bvals) != len(colors)+1:
        raise ValueError('len(boundary values) should be equal to  len(colors)+1')
    bvals = sorted(bvals)
    nvals = [(v-bvals[0])/(bvals[-1]-bvals[0]) for v in bvals]  #normalized values

    dcolorscale = [] #discrete colorscale
    for k in range(len(colors)):
        dcolorscale.extend([[nvals[k], colors[k]], [nvals[k+1], colors[k]]])
    return dcolorscale

def holidays(year):

    sorted_days = list(year.days.keys())
    sorted_days.sort()
    z = []
    for x in sorted_days:
        if year.days[x].public_holiday:
            z += [1.0]
        elif year.days[x].weekend:
            z += [3.0]
        elif year.days[x].fake_holiday:
            z += [2.0]
        else:
            z += [0.0]

    dates_in_year = sorted_days
    
    weekdays_in_year = [i.weekday() for i in dates_in_year]
    weeknumber_of_dates = [i.strftime("%Gww%V")[2:] for i in dates_in_year]
    weeknumber_of_dates_ = [int(i.strftime("%V")) for i in dates_in_year]
    month_name = [calendar.month_name[i.month] for i in dates_in_year]
    unique_month = np.unique(month_name)
    first_index_month = [weeknumber_of_dates_[np.min(np.where(np.asarray(month_name) == x)[0])] for x in unique_month]

    text = [str(i) for i in dates_in_year]
    colorscale=discrete_colorscale([0.0,1.0,2.0,3.0,4.0], ['#eeeeee', '#76cf63', '#fbb4ae', '#decbe4'])
    
    data = [
        go.Heatmap(
            x = weeknumber_of_dates_,
            y = weekdays_in_year,
            z = z,
            zmin=0,
            zmax=4,
            text=text,
            hoverinfo="text",
            xgap=3, # this
            ygap=3, # and this is used to make the grid-like apperance
            showscale=True,
            colorscale=colorscale,
            colorbar = dict(thickness=15,  len=0.7,
                tickvals=[0.5,1.5,2.5,3.5],
                ticktext=["work", "public holiday", "holiday", "weekend"]),
            )
        ]
    layout = go.Layout(
        title="Calendar year",
        height=280,
        yaxis=dict(
            showline = False, showgrid = False, zeroline = False,
            tickmode="array",
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            tickvals=[0,1,2,3,4,5,6],
        ),
        xaxis=dict(
            showline = False, showgrid = False, zeroline = False,
            tickmode="array", ticktext = unique_month, tickvals=first_index_month,
            ),
        font={"size":10, "color":"#9e9e9e"},
        plot_bgcolor=("#fff"),
        margin = dict(t=40),
        )

    fig = go.Figure(data=data, layout=layout)
    return fig


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
            html.Div([
                    html.H1(children='Working Hours Randomizer'),

                    html.Hr(),

                    html.Div([
                            html.Div([
                                html.Div(children='''What holidays will you take?'''),
                                dcc.DatePickerRange(
                                    id='my-date-picker-range2',
                                    min_date_allowed=datetime.datetime(2020, 1, 1),
                                    max_date_allowed=datetime.datetime(2020, 12, 31),
                                    start_date_placeholder_text="Start Period",
                                    end_date_placeholder_text="End Period",
                                ),
                                html.Br(),
                                html.Br(),

                                dbc.Button("Submit", id = 'button-2', outline=True, color="primary", className="mr-1"),
                                html.Br(),
                                
                                     ], className="four columns"),
                            html.Div([
                                html.Div([
                                     html.Div(
                                         [   html.Br(),
                                             html.H6(id="holidays"), html.P("Holidays left")],
                                         id="resting",
                                         className="four columns",
                                     ),
                                     html.Div(
                                         [ html.Br(),
                                           html.H6(id="worked"), html.P("Hours Worked")],
                                         id="working",
                                         className="four columns",
                                     ),
                                     html.Div(
                                         [
                                            html.Br(),
                                            html.Br(),
                                             html.A(
                                                 html.Button("Download"),
                                                 id='download-link',
                                                 download="rawdata.csv",
                                                 href="",
                                                 target="_blank",
                                             )
                                         ],
                                         className="one column",
                                         id="button",
                                     ),
                                ],
                                 id="info-container",
                                 className="row container-display",)
                                ],
                                className="eight columns"),
                            ], className="row"),

            html.Hr(),

            html.Div(id='output'),
            html.Div([], id='step_list', style={'display': 'none'})

            ], id="mainContainer", style={"margin-top": "40px", "margin-right": "40px", "margin-left": "40px", "margin-bottom": "40px", "padding":"60px"}, )
])


@app.callback(
    [dash.dependencies.Output('output', 'children'),
    dash.dependencies.Output('step_list', 'children')],
    [dash.dependencies.Input('button-2', 'n_clicks')],
    state=[dash.dependencies.State('step_list', 'children'), dash.dependencies.State('my-date-picker-range2', 'start_date'),
     dash.dependencies.State('my-date-picker-range2', 'end_date')])
def compute(n_clicks, data, start_date, end_date):
    year = fun.create_year(year=2020)

    if n_clicks is None or start_date is None or end_date is None:
        return [dcc.Graph(id="heatmap-test", figure=holidays(year), config={"displayModeBar": False}), []]
    else:
        d1 = start_date.split("-")
        d2 = end_date.split("-")
        d1 = datetime.date(int(d1[0]), int(d1[1]), int(d1[2]))
        d2 = datetime.date(int(d2[0]), int(d2[1]), int(d2[2]))
        delta = d2 - d1       # as timedelta
        
        data = [datetime.datetime.strptime(i, "%Y-%m-%d").date() for i in data]
        data = data + [d1 + datetime.timedelta(days=i) for i in range(delta.days + 1)]
        for i in data:
            year.add_fake_holiday(m = i.month, d = i.day)
        
        return [dcc.Graph(id="heatmap-test", figure=holidays(year), config={"displayModeBar": False}), data]
        

# Selectors -> well text
@app.callback(
    dash.dependencies.Output("holidays", "children"),
    [dash.dependencies.Input('output', 'children')],
            state = [
                dash.dependencies.State('step_list', 'children'),
            ],
        )
def update_holidays_text(output, data):
    year = fun.create_year(year=2020)
    data = [datetime.datetime.strptime(i, "%Y-%m-%d").date() for i in data]

    for i in data:
        year.add_fake_holiday(m = i.month, d = i.day)
    return str(year.count_holidays_left()) + " days"

# Selectors -> well text
@app.callback(
    dash.dependencies.Output("worked", "children"),
            [dash.dependencies.Input('output', 'children')],
            state = [
                dash.dependencies.State('step_list', 'children'),
            ],
        )
def update_worked_text(n_clicks, data):
    year = fun.create_year(year=2020)
    data = [datetime.datetime.strptime(i, "%Y-%m-%d").date() for i in data]

    for i in data:
        year.add_fake_holiday(m = i.month, d = i.day)
    return str(round(year.hours_worked()-year.holiday_hours(),2))

@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [dash.dependencies.Input('output', 'children')],
    state = [
        dash.dependencies.State('step_list', 'children'),
    ],)
def update_download_link(n_clicks, data):
    year = fun.create_year(year=2020)
    data = [datetime.datetime.strptime(i, "%Y-%m-%d").date() for i in data]

    for i in data:
        year.add_fake_holiday(m = i.month, d = i.day)
    csv_string = fun.generate_table_results(year)
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + quote(csv_string)
    return csv_string


if __name__ == '__main__':
    app.run_server(debug=True,port=8000, host='127.0.0.1')

