import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

from sqldatabase import SessionLocal
from sqldbapi import get_checkins_df

import plotly
import plotly.graph_objs as go

db = SessionLocal()

#@st.cache
def get_data(db):
    df_data_ref = get_checkins_df(db)
    #df_data = df_data_ref
    df_data = pd.DataFrame(df_data_ref)
    #df_data.columns = df_data_ref.columns

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
    return df_data, df_scalar, df_scalar_wk, df_text
    #return df_data


@st.cache
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
    
def update_figure(json_df,
                  parent='Chores', 
                  agg=['min', 'max', 'sum', 'count'][0], 
                  ctype='Stacked', 
                  flipxy=False, 
                  ):
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

if __name__ == '__main__':
    
    ######################
    # Processing #
    ##############

    df_data, df_scalar, df_scalar_wk, df_text = get_data(db)
    d = process_data()
    
    ######################
    # Controls #
    ############
        
    flipxy = False
    if st.checkbox('Event/Time on X-Axis'):
        flipxy = True
    
    fig = update_figure(d, flipxy=flipxy) 
    
    fig.update_layout(barmode='group')
    if st.checkbox('Grouped/Stacked'):
        fig.update_layout(barmode='stack')  
    
    ######################
    # Layout #
    ##########

    fig

    "# Checkins"

    df_data[['timestamp','event_type','value']]

    "# Checkin Comments"

    df_text[['timestamp','comments','event_type',]]

    ######################


    