import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go
from config import analysis_start_date, analysis_end_date, date_12_months_ago, this_year, first_day_last_year, same_date_last_year, weeks_left_in_year

### Functions to calculate single value metrics

# Function to calculate the yearly distances
def yearly_distance_metrics(df):
    distance_km_this_year = df[df['year']==this_year]['distance_km'].sum()
    distance_km_last_year = df[df['year']==this_year-1]['distance_km'].sum()
    distance_km_last_year_to_date = df[(df['start_date_dt']<=same_date_last_year) & (df['start_date_dt']>=first_day_last_year)]['distance_km'].sum()
    return round(distance_km_this_year), round(distance_km_last_year), round(distance_km_last_year_to_date)


# Count features
def yearly_activities_counts(df):
    this_year = datetime.today().year
    activities_this_year = df[df['year']==this_year]['id'].nunique()
    activities_last_year_to_date = df[(df['start_date_dt']<=same_date_last_year) & (df['start_date_dt']>=first_day_last_year)]['id'].nunique()
    return activities_this_year, activities_last_year_to_date

# Function to calculate pace from the speed

def calculate_pace_mm_ss(speed_in_mps):
    minutes_per_km = 1000 / (speed_in_mps * 60)
    minutes = int(minutes_per_km)
    seconds = (minutes_per_km - minutes) * 60
    seconds = int(round(seconds))
    return f"{minutes}:{seconds:02d}"

# Function to calculate weekly distance
def weekly_distance_this_and_last_year(df):
    weekly_distance = df.groupby(['year', 'week'])['distance_km'].sum().reset_index()
    weekly_distance_this_and_last_year = weekly_distance[weekly_distance['year'].isin([datetime.today().year, datetime.today().year-1])]
    return weekly_distance_this_and_last_year

# Function to get average pace by month and by long/short runs
def average_pace_by_month_and_run_type(df):
    monthly_pace = df.groupby(['month'])['average_speed_kmh'].mean().reset_index()
    monthly_pace = monthly_pace[monthly_pace['month'] >= date_12_months_ago.strftime('%Y-%m-01')]
    
    monthly_pace_by_long_run = df.groupby(['month', 'is_long_run'])['average_speed_kmh'].mean().reset_index()
    monthly_pace_by_long_run = monthly_pace_by_long_run[monthly_pace_by_long_run['month'] >= date_12_months_ago.strftime('%Y-%m-01')]

    chart_data = monthly_pace[['month', 'average_speed_kmh']].rename(columns={'average_speed_kmh': 'All Runs'})

    # Add Long Runs data
    long_runs = monthly_pace_by_long_run[monthly_pace_by_long_run['is_long_run'] == True]
    chart_data = chart_data.merge(long_runs[['month', 'average_speed_kmh']], on='month', how='left')
    chart_data = chart_data.rename(columns={'average_speed_kmh': 'Long Runs'})
    
    # Add Short Runs data
    short_runs = monthly_pace_by_long_run[monthly_pace_by_long_run['is_long_run'] == False]
    chart_data = chart_data.merge(short_runs[['month', 'average_speed_kmh']], on='month', how='left')
    chart_data = chart_data.rename(columns={'average_speed_kmh': 'Short Runs'})
    
    # Set month as index
    chart_data = chart_data.set_index('month')

    # return monthly_pace, monthly_pace_by_long_run
    return chart_data

# Function for pace per hour of the day
def pace_per_hour_of_day(df):
    pace_by_hour = df[df['year']==this_year].groupby('hour_of_day')['average_speed_kmh'].mean().reset_index()
    pace_by_hour['average_speed_kmh'] = pace_by_hour['average_speed_kmh'].round(1)

    activities_by_hour = df[df['year']==this_year].groupby('hour_of_day')['id'].count().reset_index()
    activities_by_hour.columns = ['hour_of_day', 'nbr_of_activities']

    return pace_by_hour, activities_by_hour

# Function to get the top performances (longest, most ascent, fastest)
def get_record_activities(df):
    longest_runs = df.groupby(df['start_date_dt'].dt.year)['distance_km'].max().reset_index().sort_values(by='start_date_dt', ascending=False)
    longest_runs['Personal Best'] = 'Longest Run (km)'
    longest_runs = longest_runs[['Personal Best', 'start_date_dt', 'distance_km']]
    longest_runs_pivot = longest_runs.pivot(index='Personal Best', columns='start_date_dt', values='distance_km')
    
    biggest_ascent = df.groupby(df['start_date_dt'].dt.year)['total_elevation_gain'].max().reset_index().sort_values(by='start_date_dt', ascending=False)
    biggest_ascent['Personal Best'] = 'Most Ascent (m)'
    biggest_ascent = biggest_ascent[['Personal Best', 'start_date_dt', 'total_elevation_gain']]
    biggest_ascent_pivot = biggest_ascent.pivot(index='Personal Best', columns='start_date_dt', values='total_elevation_gain')

    fastest_10k = df[df['distance_km'] >= 10].groupby(df['start_date_dt'].dt.year)['average_speed_kmh'].max().reset_index().sort_values(by='start_date_dt', ascending=False)
    fastest_10k['Personal Best'] = 'Fastest 10k (km/h)'
    fastest_10k = fastest_10k[['Personal Best', 'start_date_dt', 'average_speed_kmh']] 
    fastest_10k_pivot = fastest_10k.pivot(index='Personal Best', columns='start_date_dt', values='average_speed_kmh')

    personal_bests = pd.concat([longest_runs_pivot, biggest_ascent_pivot, fastest_10k_pivot])
    return personal_bests







# Function to process cumulative Strava data. The df_activities has to be 
# processed by the process_strava_data function and filtered by activity before 
# being passed to this function.

def get_cumulative_strava_data(df_activities):
    # Create a date range
    date_range = pd.date_range(start=analysis_start_date, end=analysis_end_date, freq='D')

    # Create a DataFrame
    df_dates = pd.DataFrame(date_range, columns=['date'])

    # Join the activities and 
    df = pd.merge(df_dates, df_activities, left_on='date', right_on='start_date_dt', how='left')
    df['distance'] = df['distance'].fillna(0)
    df['cumulative_distance'] = df['distance'].cumsum()
    df['cumulative_distance_km'] = df['cumulative_distance']/1000

    df['cumulative_sum_by_year'] = df.groupby('year')['distance'].cumsum()
    df['cumulative_sum_by_year_km'] = df['cumulative_sum_by_year']/1000
    return df

def create_activity_heatmap(df):
    # Create a pivot table with day of week as rows and week number as columns
    heatmap_data = df.pivot_table(
        index=df['day_of_week'],
        columns=df['start_date'].dt.isocalendar().week,
        values='id',
        aggfunc='count'
    ).fillna(0)

    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale='YlOrRd'
    ))

    fig.update_layout(
        title='Activity Frequency Heatmap',
        xaxis_title='Week of Year',
        yaxis_title='Day of Week'
    )

    return fig

