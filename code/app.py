# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import functions as fun
import calmap
import json
import plotly
import datetime
import calendar
import plotly.graph_objs as go
import numpy as np
from datetime import datetime as dt
import dash
import dash_html_components as html
import dash_core_components as dcc
import re

year = fun.create_year(year=2020)

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

    sorted_days = year.days.keys()
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
            colorbar = dict(thickness=15,
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


app.layout = html.Div([
            html.Div([
                    html.H1(children='Working Hours Randomizer'),

                    html.Hr(),

                    html.Div([
                            html.Div([
                                html.Div(children='''What holidays will you take?'''),
                                dcc.DatePickerRange(
                                    id='my-date-picker-range2',
                                    min_date_allowed=min(year.days),
                                    max_date_allowed=max(year.days),
                                    initial_visible_month=min(year.days),
                                    end_date=min(year.days),
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
                                           html.H6(id="worked"), html.P("Worked")],
                                         id="working",
                                         className="four columns",
                                     ),
                                     html.Div(
                                         [
                                            html.Br(),
                                            html.Br(),
                                             html.A(
                                                 html.Button("Download", id="learn-more-button"),
                                                 href="https://plot.ly/dash/pricing/",
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
            html.Br(),
            html.Br(),

            ], id="mainContainer", style={"margin-top": "25px", "margin-right": "25px", "margin-left": "25px", "margin-bottom": "25px", "padding":"20px"}, )
])


@app.callback(
    dash.dependencies.Output('output', 'children'),
    [dash.dependencies.Input('button-2', 'n_clicks')],
    state=[dash.dependencies.State('my-date-picker-range2', 'start_date'),
     dash.dependencies.State('my-date-picker-range2', 'end_date')])
def compute(n_clicks, start_date, end_date):
    if n_clicks is None or start_date is None or end_date is None:
        return [dcc.Graph(id="heatmap-test", figure=holidays(year), config={"displayModeBar": False})]
    else:
        d1 = start_date.split("-")
        d2 = end_date.split("-")
        d1 = datetime.date(int(d1[0]), int(d1[1]), int(d1[2]))
        d2 = datetime.date(int(d2[0]), int(d2[1]), int(d2[2]))
        delta = d2 - d1       # as timedelta

        for i in range(delta.days + 1):
            day = d1 + datetime.timedelta(days=i)
            year.add_fake_holiday(m = day.month, d = day.day, name = "New", hours_worked = 0)
            
        return [dcc.Graph(id="heatmap-test", figure=holidays(year), config={"displayModeBar": False})]
        
        
# Selectors -> well text
@app.callback(
    dash.dependencies.Output("holidays", "children"),
            [
                dash.dependencies.Input("output", "children"),
            ],
        )
def update_holidays_text(output):
    return str(year.count_holidays_left()) + " days"

# Selectors -> well text
@app.callback(
    dash.dependencies.Output("worked", "children"),
            [
                dash.dependencies.Input("output", "children"),
            ],
        )
def update_worked_text(output):
    return str(year.hours_worked()) + " hours"



if __name__ == '__main__':
    app.server.run(port=8000, host='127.0.0.1')
