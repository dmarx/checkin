"""
Just copying this example for now: 

	https://www.reddit.com/r/FastAPI/comments/gmdkhj/how_can_i_use_fastapi_with_plotly_dash/ftcxe2d/
  
Another good prospect (which looks like it's using basically the same strategy with WSGIMiddleware):

	https://gist.github.com/dmontagu/b89821fc64101f2143ddc256103eca59
 
"""

import dash
import dash_core_components as dcc
import dash_html_components as html

# Create the Dash application, make sure to adjust requests_pathname_prefx
app_dash = dash.Dash(__name__, requests_pathname_prefix='/dash/')


from sqldatabase import SessionLocal
from sqldbapi import get_checkins_df

db = SessionLocal()
df_data = get_checkins_df(db)

idx_valued = df_data['value'].notnull()
idx_text = df_data['comments'].notnull()

df_text   = df_data[idx_text]
df_scalar = df_data[idx_valued]

df_scalar_wk = (df_scalar
                    .groupby([df_scalar['timestamp'].dt.week, 'parent', 'event_type'])
                    ['value']
                    #.count()
                    .agg(['min', 'max', 'sum', 'count'])
                    .reset_index()
                    .rename(columns={'timestamp':'week'})
               )

df_scalar_day = (df_scalar
                    .groupby([df_scalar['timestamp'].dt.day, 'parent', 'event_type'])
                    ['value']
                    #.count()
                    .agg(['min', 'max', 'sum', 'count'])
                    .reset_index()
                    .rename(columns={'timestamp':'day'})
               )



import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly
import plotly.graph_objs as go

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
        )  
    ]),
    dcc.Graph(id='graph'),
])


# Define callback to update graph
@app_dash.callback(Output('graph', 'figure'),
             [Input('parent-dropdown', 'value'),
              Input('agg-dropdown', 'value'),
              Input('chart-type', 'value'),
              Input('checkbox-flip-xy', 'value')
             ])
def update_figure(parent, agg, ctype, flipxy):
    df_sub1 = df_scalar_wk[df_scalar_wk['parent'] == parent]
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