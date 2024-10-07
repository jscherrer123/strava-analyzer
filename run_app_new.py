import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt
import plotly.graph_objs as go
from datetime import datetime, timedelta
import statsmodels.api as sm

from src.data.fetch_strava_data import fetch_strava_activities
from src.data.process_data import process_strava_data
from src.transformations.transform_data import yearly_distance_metrics, yearly_activities_counts, calculate_pace_mm_ss, weekly_distance_this_and_last_year, average_pace_by_month_and_run_type, pace_per_hour_of_day, get_record_activities, get_cumulative_strava_data, create_activity_heatmap
from src.visualizations.visualize_data import lineplot, barplot, scatterplot

from config import analysis_start_date, analysis_end_date, date_12_months_ago, this_year, first_day_last_year, same_date_last_year, weeks_left_in_year


def run_app():
    activities = fetch_strava_activities()
    activities = process_strava_data(activities)
    # st.dataframe(activities, use_container_width=True)

    activity_type_list = ['Run', 'Hike', 'Ride', 'MountainBikeRide', 'AlpineSki', 'BackcountrySki', 'NordicSki', 'Workout']
    # # activity_type_list = activities['type'].unique().tolist()

    # Streamlit code for generating title, subtitle, and sections
    st.title("🏃‍♂️Your Strava Master Dashboard🏃‍♂️")
    st.write("Discovery everything you didn't know about your Strava data!")

    ### Section 1: Input activity type
    st.write("Before we start: Choose the activity type you want to analyse")
    activity_type = st.selectbox("Select Activity Type", activity_type_list)

    act_to_analyse = activities[activities['sport_type'] == activity_type]

    # Add run-specific functions
    act_to_analyse['is_long_run'] = act_to_analyse['distance_km'] > 10
    act_to_analyse['pace'] = act_to_analyse['average_speed'].apply(calculate_pace_mm_ss)

    # Get the number of activities this and last year, and the distance this and last year
    act_this_year, act_last_year_to_date = yearly_activities_counts(act_to_analyse)
    dist_km_this_year, dist_km_last_year, dist_km_last_year_to_date = yearly_distance_metrics(act_to_analyse)

    ## Ask the user for their running goal
    st.markdown(f"### Do you have a running goal for this year?")
    goal_distance = 0
    goal_distance = st.number_input(f"Last year, you ran :orange[{dist_km_last_year}] km in total. How many km's do you want to run this year?", value=0, placeholder="Type a km distance...")

    if(goal_distance > 0):
        pct_of_yearly_goal = round((dist_km_this_year / goal_distance) * 100)
        st.write(f"### :blue[{pct_of_yearly_goal}%] of your yearly goal completed so far!")
        st.write(f"To complete your goal this year, you need to run :blue[{round((goal_distance - dist_km_this_year) / weeks_left_in_year)} km] per week.")    

    ## Start displaying stats
    st.markdown(f"### This year you have run: \n # :blue[{act_this_year}] times & :blue[{dist_km_this_year}] km \n On this day last year, you had run :orange[{act_last_year_to_date}] times and :orange[{dist_km_last_year_to_date}] km.")

    ## Display the last few runs
    st.markdown("### Your latest runs:")

    workout_cols = ['start_date', 'name', 'distance_km', 'total_elevation_gain', 'average_speed_kmh', 'pace', 'average_heartrate', 'is_over_10k']
    st.dataframe(act_to_analyse[workout_cols], use_container_width=True) 

    st.markdown("### Your weekly distance this year vs last year:")
    ## Make a line plot of the weekly km distance, for the current and previous year
    weekly_distance = weekly_distance_this_and_last_year(act_to_analyse[['year', 'week', 'distance_km']])

    # lineplot(df, x, y, color, title, x_title, y_title)
    lineplot(weekly_distance, 'week', 'distance_km', 'year', 'Weekly Distance km', 'Week', 'Weekly Distance km')
    
    st.markdown("### Compare how much you've run this year vs last year:")
    
    ## Make cumulative distance plots
    acts_cumu = get_cumulative_strava_data(act_to_analyse)

    # lineplot(df, x, y, color, title, x_title, y_title)
    lineplot(acts_cumu, 'day_of_year', 'cumulative_sum_by_year_km', 'year', 'Cumulative Distance km', 'Day of Year', 'Cumulative Distance km')

    st.markdown("### Your Personal Bests by Year:")
    personal_bests = get_record_activities(act_to_analyse)
    st.dataframe(personal_bests)

    ## Make a line plot of the average pace by month, and by long/short run
    st.markdown("### Your average pace by month, the last 12 months:")
    st.line_chart(average_pace_by_month_and_run_type(act_to_analyse))

    ## Check the activities and average pace by hour of day. 
    pace_by_hour, activities_by_hour = pace_per_hour_of_day(act_to_analyse)
    
    st.markdown(f"### Activities by the hour of day (in :blue[{this_year}]):")
    barplot(activities_by_hour, 'hour_of_day', 'nbr_of_activities', 'Activities by Hour of Day', 'Hour of Day', 'Number of Activities')

    st.markdown(f"### Your average pace by hour of day (in :blue[{this_year}]):")
    barplot(pace_by_hour, 'hour_of_day', 'average_speed_kmh', 'Average Pace by Hour of Day', 'Hour of Day', 'Average Speed (km/h)')

    ## Activity heatmap
    st.markdown(f"### Activity heatmap:")
    st.plotly_chart(create_activity_heatmap(act_to_analyse))

    ## elevation analysis
    st.markdown(f"### How does elevation affect your pace?")
    
    # Check relationship between elevation gain and speed
    scatterplot(act_to_analyse, 'elevation_gain_per_km', 'average_speed_kmh', 'Speed vs Elevation Gain', 'Elevation Gain per km', 'Average Speed (km/h)')
    # fig = px.scatter(act_to_analyse, x='elevation_gain_per_km', y='average_speed_kmh', 
    #                  title='Speed vs Elevation Gain', trendline='ols', trendline_color_override='darkgreen')
    # fig.update_layout(xaxis_title='Elevation Gain per km', yaxis_title='Average Speed (km/h)')
    # st.plotly_chart(fig)

    # Check relationship between speed and heartrate
    scatterplot(act_to_analyse, 'average_speed_kmh', 'average_heartrate', 'Speed vs Heartrate', 'Average Speed (km/h)', 'Average Heartrate (BPM)')

if __name__ == '__main__':
    run_app()