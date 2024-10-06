import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import analysis_start_date, analysis_end_date, date_12_months_ago, this_year, first_day_last_year, same_date_last_year, weeks_left_in_year

from src.data.fetch_strava_data import fetch_strava_activities

### Function to process the Strava data
def process_strava_data(df):

    # Formatting and adding appropriate date columns
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    df['start_date_dt'] = pd.to_datetime(df['start_date']).dt.strftime('%Y-%m-%d')
    df['start_date_dt'] = pd.to_datetime(df['start_date_dt'])

    # Add date and time columns
    df['year'] = df['start_date_dt'].dt.year
    df['month'] = df['start_date_dt'].apply(lambda x: x.strftime('%Y-%m-01'))
    df['week'] = df['start_date_dt'].dt.strftime('%U')
    df['day'] = df['start_date_dt'].dt.day
    df['day_of_year'] = df['start_date_dt'].dt.dayofyear
    df['hour_of_day'] = df['start_date_local'].dt.hour
    df['day_of_week'] = df['start_date_dt'].dt.dayofweek

    # Add distance features
    df['distance_km'] = df['distance']/1000
    df['average_speed_kmh'] = df['average_speed'] * 3.6

    # Add speed and pace features
    df['average_speed_kmh'] = df['average_speed'] * 3.6

    df['elevation_gain_per_km'] = df['total_elevation_gain'] / df['distance_km']

    # Add distance dummies for long run
    df['is_over_10k'] = df['distance_km'] > 10
    df['is_over_20k'] = df['distance_km'] > 20

    return df
