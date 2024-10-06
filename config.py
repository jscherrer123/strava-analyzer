from datetime import datetime, timedelta

# Global Date variables
analysis_start_date = '2022-01-01'
analysis_end_date = datetime.today().strftime('%Y-%m-%d')
date_12_months_ago = datetime.now() - timedelta(days=365)
this_year = datetime.today().year
first_day_last_year = datetime.today().replace(year=this_year-1, month=1, day=1)
same_date_last_year = datetime.today().replace(year=this_year-1)
weeks_left_in_year = 52 - int(datetime.today().strftime('%U'))