### This file contains the code used to fetch data from the Strava API
import os
from dotenv import load_dotenv
import requests
import urllib3
import pandas as pd
from pandas import json_normalize
import streamlit as st

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_strava_activities():

    # Load environment variables
    load_dotenv()

    # Load Strava API credentials from .env file
    # STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
    # STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
    # STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

    STRAVA_CLIENT_ID = st.secrets["strava"]["STRAVA_CLIENT_ID"]
    STRAVA_CLIENT_SECRET = st.secrets["strava"]["STRAVA_CLIENT_SECRET"]
    STRAVA_REFRESH_TOKEN = st.secrets["strava"]["STRAVA_REFRESH_TOKEN"]

    # Check if the environment variables are loaded correctly
    if not all([STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN]):
        raise ValueError("Missing one or more environment variables for Strava API access.")
    
     # Strava auth and activities URL
    auth_url = "https://www.strava.com/oauth/token"
    activities_url = "https://www.strava.com/api/v3/athlete/activities"

    # Payload for getting the access token 
    payload = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'refresh_token': STRAVA_REFRESH_TOKEN,
        'grant_type': "refresh_token",
        'f': 'json'
    }

    # Request access token
    print("Requesting Token...\n")
    res = requests.post(auth_url, data=payload, verify=False)

    access_token = res.json()['access_token']
    
    if not access_token:
        raise Exception("Access token not found in the response.")

    print("Access Token = {}\n".format(access_token))

    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 200, 'page': 1}



    # Fetch data until there are no more activities

    all_activities = []
        
    while True:
        response = requests.get(activities_url, headers=header, params=param).json()
        
        if not response:  # If the response is empty, we've reached the end of the data
            break
        
        all_activities.extend(response)
        print(f"Retrieved page {param['page']}")
        
        if len(response) < 200:  # If we got less than 200 activities, it's the last page
            break
        
        param['page'] += 1  # Move to the next page

    activities = json_normalize(all_activities)

    return activities
