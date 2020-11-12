import requests
import pandas as pd


# base URL to which we'll append given fin IDs
fin_url_base = 'http://surf.smartfin.org/fin/'

# Look for the following text in the HTML contents in fcn below
str_id_ride = 'rideId = \'' # backslash allows us to look for single quote
str_id_date = 'var date = \'' # backslash allows us to look for single quote

# Base URL to which we'll append given ride IDs
ride_url_base = 'https://surf.smartfin.org/ride/'

# Look for the following text in the HTML contents in fcn below
str_id_csv = 'img id="temperatureChart" class="chart" src="' 

class SmartfinScraper:

    def __init__(self):
        print("web scraper initialized")

    
    def get_csv_from_ride_id (self, ride_id):
        # Build URL for each individual ride
        ride_url = ride_url_base+str(ride_id)
        print(f'fetching ride from: {ride_url}')

        # Get contents of ride_url
        html_contents = requests.get(ride_url).text

        # Find CSV identifier 
        loc_csv_id = html_contents.find(str_id_csv)

        # Different based on whether user logged in with FB or Google
        offset_googleOAuth = [46, 114]
        offset_facebkOAuth = [46, 112]
        if html_contents[loc_csv_id+59] == 'f': # Facebook login
            off0 = offset_facebkOAuth[0]
            off1 = offset_facebkOAuth[1]
        else: # Google login
            off0 = offset_googleOAuth[0]
            off1 = offset_googleOAuth[1]

        csv_id_longstr = html_contents[loc_csv_id+off0:loc_csv_id+off1]
        
        # Stitch together full URL for CSV
        # other junk URLs can exist and break everything
        if ("media" in csv_id_longstr) & ("Calibration" not in html_contents): 

            sample_interval = '1000ms'

            mdf_url = f'https://surf.smartfin.org/{csv_id_longstr}Motion.CSV'
            print(f'fetching motion data from: {mdf_url}')
            mdf = pd.read_csv(mdf_url, parse_dates = [0])
            mdf = mdf.set_index('UTC', drop = True, append = False)
            mdf = mdf.resample(sample_interval).mean()
            odf_url = f'https://surf.smartfin.org/{csv_id_longstr}Ocean.CSV'
            print(f'fetching ocean data from: {odf_url}')
            odf = pd.read_csv(odf_url, parse_dates = [0])
            odf = odf.set_index('UTC', drop = True, append = False)
            odf = odf.resample(sample_interval).mean()

            return mdf, odf

        else:
            print('here')
            df = pd.DataFrame() # empty DF just so something is returned
            return df, df
      
    