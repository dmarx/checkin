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
app_dash.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5],
                    'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])