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

def get_data(db):
    df_data = get_checkins_df(db)
    idx_valued = df_data['value'].notnull()
    idx_text = df_data['comments'].notnull()
    df_text   = df_data[idx_text]
    df_scalar = df_data[idx_valued]
    return df_data, df_scalar, df_text

@st.cache
def apply_date_filter(df, 
                 dt_start=None,
                 dt_end=None):
    if dt_start is None:
        dt_start = df['timestamp'].min()
    if dt_end is None:
        dt_end = df['timestamp'].max()
    df = df[dt_start <= df['timestamp']]
    df = df[df['timestamp'] <= dt_end]
    return df

@st.cache
def process_data(df, dtagg='week'):
    aggs = ['min', 'max', 'sum', 'count']
    if dtagg=='week':
        dt_agg= df['timestamp'].dt.week
    elif dtagg=='day':
        dt_agg= df['timestamp'].dt.day
    grpd = df.groupby([dt_agg, 'parent', 'event_type'])
    outv = grpd['value'].agg(aggs).reset_index().rename(columns={'timestamp':dtagg})
    return outv
    
@st.cache
def filter_parent(df, parent='Chores'):
    return df[df['parent'] == parent]
    
def update_figure(df,
                  agg=['sum', 'max', 'min', 'count'][0], 
                  ctype='Stacked', 
                  flipxy=False, 
                  parent='Chores'
                  ):
    traces = []
    xcol = 'week'
    grpcol = 'event_type'
    if flipxy:
        xcol, grpcol = grpcol, xcol
    for event_type, subset in df.groupby(grpcol):
        trace = go.Bar(x=subset[xcol],
                       y=subset[agg],
                       name=event_type
                         ) 
        traces.append(trace)
    layout = go.Layout(hovermode='closest', title=parent)
    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(barmode=ctype)        
    return fig
    
def calendar_plot(df,
                  agg=['sum', 'min', 'max', 'count'][0], 
                  parent='Chores'
                  ):
    process_data(df, dtagg='day')
    pass

if __name__ == '__main__':
    
    ######################
    # Processing #
    ##############

    #df_data, df_scalar , df_scalar_wk, df_text = get_data(db)
    df_data, df_scalar, df_text = get_data(db)
    #df_data, df_scalar, df_text = get_data()
    df = apply_date_filter(df_scalar)
    
    
    ######################
    # Controls #
    ############
    
    parent = st.sidebar.selectbox('Event Parent Type', df['parent'].unique())
    df = filter_parent(df, parent)
    
    flipxy = False
    if st.sidebar.checkbox('Event/Time on X-Axis'):
        flipxy = True
        
    ctype='group'
    if st.sidebar.checkbox('Grouped/Stacked'):
        ctype='stack'
    
    df = process_data(df)
    fig = update_figure(df, flipxy=flipxy, ctype=ctype)  
    
    ######################
    # Layout #
    ##########

    fig
    
    data_container = st.beta_container()
    col1, col2 = st.beta_columns(2)
    with data_container:
        with col1:
            "# Checkins"
            df_data[['timestamp','event_type','value']]
        with col2:
            "# Checkin Comments"
            df_text[['timestamp','comments','event_type',]]

    ######################


    