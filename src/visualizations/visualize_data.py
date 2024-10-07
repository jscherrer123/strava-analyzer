import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt
import plotly.graph_objs as go

def lineplot(df, x, y, color, title, x_title, y_title):
    fig = px.line(df, x=x, y=y, title=title, color=color)
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    st.plotly_chart(fig)

def barplot(df, x, y, title, x_title, y_title):
    fig = px.bar(df, x=x, y=y, title=title, color=y, text=y)
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    st.plotly_chart(fig)

def scatterplot(df, x, y, title, x_title, y_title, year=None):
    fig = px.scatter(df, x=x, y=y, title=title, trendline='ols', trendline_color_override='darkgreen', color = year)
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    st.plotly_chart(fig)
