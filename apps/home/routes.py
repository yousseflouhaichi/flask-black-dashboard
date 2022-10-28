# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

@blueprint.route('/index')
@login_required
def index():
    import os
    # print(os.getcwd())
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    print(BASE_DIR)
    file_path = os.path.join(BASE_DIR, 'data\EURUSD_M15.csv')
    print(file_path)
    df = pd.read_csv(file_path)
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    print('*****************************')
    print(df)
    print('*****************************')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df.high, mode='lines', name='high'))
    fig.add_trace(go.Scatter(x=df.index, y=df.low, mode='lines', name='low'))
    fig.add_trace(go.Scatter(x=df.index, y=df.open, mode='lines', name='open'))
    fig.add_trace(go.Scatter(x=df.index, y=df.close, mode='lines', name='close'))

    # fig.layout.xaxis.type = 'category'

    fig.update_layout(
        # width=1100,
        # height=400,
        autosize=True,
        # xaxis_tickformat = '%d %B (%a)<br>%Y'
    )

    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
            # dict(values=["2015-12-25", "2016-01-01"])  # To hide holidays
        ]
    )

    data = fig.to_html(config={'displaylogo': False, 'modeBarButtonsToRemove': ['Boxselect', 'lasso2d', "select2d"]})
    context = {'data': data}

    return render_template('home/index.html', segment='index', context=context)


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
