"""
Just copying this example for now: 

	https://www.reddit.com/r/FastAPI/comments/gmdkhj/how_can_i_use_fastapi_with_plotly_dash/ftcxe2d/
  
Another good prospect (which looks like it's using basically the same strategy with WSGIMiddleware):

	https://gist.github.com/dmontagu/b89821fc64101f2143ddc256103eca59
 
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from sqldatabase import SessionLocal
from sqldbapi import get_checkins_df
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly
import plotly.graph_objs as go

app_dash = dash.Dash(__name__, requests_pathname_prefix='/dash/')

def fetch_data(db):
    
    df_data = get_checkins_df(db)

    idx_valued = df_data['value'].notnull()
    idx_text = df_data['comments'].notnull()

    df_text   = df_data[idx_text]
    df_scalar = df_data[idx_valued]

    df_scalar_wk = (df_scalar
                        .groupby([df_scalar['timestamp'].dt.week, 'parent', 'event_type'])
                        ['value']
                        .agg(['min', 'max', 'sum', 'count'])
                        .reset_index()
                        .rename(columns={'timestamp':'week'})
                   )

    df_scalar_day = (df_scalar
                        .groupby([df_scalar['timestamp'].dt.day, 'parent', 'event_type'])
                        ['value']
                        .agg(['min', 'max', 'sum', 'count'])
                        .reset_index()
                        .rename(columns={'timestamp':'day'})
                   )
    return df_text, df_scalar, df_scalar_wk, df_scalar_day

@app_dash.callback(Output('df_processed', 'children'),
                  [Input('my-date-picker-range', 'start_date'),
                   Input('my-date-picker-range', 'end_date')])
def process_data(#df, 
                 dt_start=None,
                 dt_end=None
                ):
    aggs = ['min', 'max', 'sum', 'count']
    df = df_scalar.copy()
    #print(dt_start, dt_end)
    if dt_start is None:
        dt_start = df['timestamp'].min()
    if dt_end is None:
        dt_end = df['timestamp'].max()
    #print(dt_start, dt_end)
    #df = df[dt_start <= df['timestamp'] <= dt_end]
    df = df[dt_start <= df['timestamp']]
    df = df[df['timestamp'] <= dt_end]
    dt_agg= df['timestamp'].dt.week
    grpd = df.groupby([dt_agg, 'parent', 'event_type'])
    outv = grpd['value'].agg(aggs).reset_index().rename(columns={'timestamp':'week'})
    #print(outv['week'].min(), outv['week'].max())
    #print("data processed")
    return outv.to_json(None)
    

# Define callback to update graph
@app_dash.callback(Output('graph', 'figure'),
             [Input('parent-dropdown', 'value'),
              Input('agg-dropdown', 'value'),
              Input('chart-type', 'value'),
              Input('checkbox-flip-xy', 'value'),
              Input('df_processed', 'children')
             ])
def update_figure(parent, agg, ctype, flipxy, json_df):
    df_sub1 = pd.read_json(json_df)
    df_sub1 = df_sub1[df_sub1['parent'] == parent]
    traces = []
    xcol = 'week'
    grpcol = 'event_type'
    if flipxy:
        xcol, grpcol = grpcol, xcol
    for event_type, subset in df_sub1.groupby(grpcol):
        trace = go.Bar(x=subset[xcol],
                       y=subset[agg],
                       name=event_type
                         ) 
        traces.append(trace)
    layout = go.Layout(hovermode='closest', title=parent)
    fig = go.Figure(data=traces, layout=layout)
    if ctype == 'Stacked':
        fig.update_layout(barmode='stack')        
    return fig
    
#######################

# Create the Dash application, make sure to adjust requests_pathname_prefx
db = SessionLocal()
df_text, df_scalar, df_scalar_wk, df_scalar_day = fetch_data(db)

app_dash.layout = html.Div([
    html.H1("Checkin data grouped by week"),
    html.Label([
        "Parent",
        dcc.Dropdown(
            id='parent-dropdown', clearable=False,
            value='Chores', options=[
                {'label': c, 'value': c}
                for c in df_scalar_wk['parent'].unique()
            ]),
        dcc.RadioItems(
            id='agg-dropdown', 
            #clearable=False,
            value='count', options=[
                {'label': c, 'value': c}
                for c in ['min', 'max', 'sum', 'count']
            ]),
        dcc.RadioItems(
                id='chart-type',
                options=[{'label': i, 'value': i} for i in ['Grouped', 'Stacked']],
                value='Grouped',
                #labelStyle={'display': 'inline-block'}
            ),
        dcc.RadioItems(
            id='checkbox-flip-xy',
            options=[
                {'label': 'Event on X', 'value': 1},
                {'label': 'Time on X', 'value':0}
            ],
            value=0
        ),
    dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=df_scalar['timestamp'].min(),
            max_date_allowed=df_scalar['timestamp'].max(),
            start_date=df_scalar['timestamp'].min(),
            end_date=df_scalar['timestamp'].max()
        ),    
        # Hidden div inside the app that stores the intermediate value
        html.Div(id='df_processed', style={'display': 'none'})
    ]),
    dcc.Graph(id='graph'),
    
])