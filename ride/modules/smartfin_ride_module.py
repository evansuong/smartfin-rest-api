import requests

from .double_integral_bandpass import double_integral_bandpass_filter
from .smartfin_web_scrape import SmartfinScraper
from .cdip_web_scrape import CDIPScraper



"""
Smartfin Web Scrape API is an interface that allows smartfin users to get data of their smartfin ride. This module interacts with both the smartfin website and CDIP THREDDS API to get smartfin and CDIP data. 
"""
class RideModule:
    
    def __init__(self): 
        print('ride initialized')

        
    # MAIN RIDE FUNCTION
    def get_ride_data(self, ride_id, buoys):
        """
        adds a ride dataframe to this dictionary 
        
        """

        sWebScrape = SmartfinScraper()
        mdf, odf = sWebScrape.get_csv_from_ride_id(ride_id)

        if len(mdf) == 0 or len(odf) == 0:
            print('ERROR: Ride has no valid data, returning...')
            return {}, {}

        mdf = mdf.apply(
            lambda reading: 
                reading / 512 * 9.80665 - 9.80665 
                if reading.name == 'IMU A2'
                else reading)
        
        mdf = mdf.apply(
            lambda reading: 
                reading / 512 * 9.80665
                if reading.name == 'IMU A1' or reading.name == 'IMU A3'
                else reading)

        latitude = mdf['Latitude'].mean() / 100000
        longitude = mdf['Longitude'].mean() / 100000
                       
        #Drop the latitude and longitude values since most of them are Nan:
        mdf_dropped = mdf.drop(['Latitude', 'Longitude'], axis=1)

        #Drop the NAN values from the motion data:
        mdf = mdf_dropped.dropna(axis=0, how='any')
                   
        # convert time into seconds
        mdf['Time'] = [time / 1000 for time in mdf['Time']]
        mdf['Timestamp'] = [dateTime.timestamp() for dateTime in mdf.index]

        odf_dropped = odf.drop(['salinity', 'Calibrated Salinity', 'Salinity Stable', 'pH', 'Calibrated pH', 'pH Stable'], axis=1)
        odf = odf_dropped.dropna(axis=0, how='any')
        print('df length before water data: ', len(mdf))
        mdf, odf = self.get_water_data(mdf, odf) 
        print('df length after water data: ', len(mdf))

        # get timeframe
        start_time, end_time = self.get_timeframe(mdf)
        print(f'calculated start_time: {start_time}')
        print(f'calculated end_time: {end_time}')
        
        cWebScrape = CDIPScraper()
        mean_CDIP, means_CDIP, temp_CDIP, temps_CDIP, nearest_CDIP = cWebScrape.CDIP_web_scrape(start_time, end_time, latitude, longitude, buoys)
        print(f'retrieved nearest CDIP buoy: {nearest_CDIP}')
        print(f'retrieved CDIP mean height for ride: {mean_CDIP}')
        print(f'retrieved CDIP mean temp for ride: {temp_CDIP}')

        height_smartfin, height_list, height_sample_rate = self.calculate_ride_height(mdf)
        temp_smartfin, temp_list, temp_sample_rate = self.calculate_ride_temp(odf)

        print('uploading ride data to database...')

        loc1, loc2, loc3 = self.get_nearest_city(latitude, longitude)
        
        mdf = mdf.drop(['Time'], axis=1)
        mdf = mdf.set_index('Timestamp')


        # compress dataframes and save path
        mdf_path = f"ride/motion_dfs/{ride_id}_mdf.csv"
        odf_path = f"ride/ocean_dfs/{ride_id}_odf.csv"

        mdf.to_csv(mdf_path)
        odf.to_csv(odf_path)

        # format data into dict for ride model
        data = {
            'rideId': ride_id, 
            'loc1': loc1,
            'loc2': loc2,
            'loc3': loc3,
            'startTime': int(start_time),
            'endTime': int(end_time),
            'heightSmartfin': height_smartfin,
            'tempSmartfin': temp_smartfin,
            'buoyCDIP': nearest_CDIP, 
            'heightCDIP': mean_CDIP, 
            'tempCDIP': temp_CDIP, 
            'latitude': latitude,
            'longitude': longitude,
        }

        dfs = {
            'motionData': mdf_path,
            'oceanData': odf_path,
        }
    
        return data, dfs
     
    

    # HELPER FUNCTIONS    
    # these two functions are temporary and will be edited when we refine them
    def calculate_ride_height(self, mdf): 
        
        filt = double_integral_bandpass_filter()
        height_smartfin, height_list, height_sample_rate = filt.calculate_ride_height(mdf)

        print(f'calculated smartfin significant wave height: {height_smartfin}')
        print(f'height reading sample rate: {height_sample_rate}')
        return height_smartfin, height_list, height_sample_rate 


    def calculate_ride_temp(self, odf):
        temps = odf['Calibrated Temperature 1']
        temp = temps.mean()
        temps = list(temps)
        print(f'calculated smartfin ride temp: {temp}')
        tempSampleRate = (int(odf.iloc[1]['Time']) - int(odf.iloc[0]['Time'])) / 1000
        print(f'temperature reading sample rate: {tempSampleRate}')

        return temp, temps, tempSampleRate


    def get_nearest_city(self, latitude, longitude):
        key = "AIzaSyCV3zZ2YhNOsf9DN8CvSiH1NBJC3XdMYs4"
        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&sensor=true&key={key}'
        response = requests.get(url).json()
        loc1 = (response['results'][0]['address_components'][2]['long_name'])
        loc2 = (response['results'][0]['address_components'][3]['long_name'])
        loc3 = (response['results'][0]['address_components'][4]['long_name'])
        
        return loc1, loc2, loc3


    
    # filter motion and ocean dataframes to only hold readings taken from when the surfer is in the water
    def get_water_data(self, mdf, odf):

        temps = odf['Calibrated Temperature 1']
        threshold = temps.std() / 2
        med = temps.median()

        mdf, odf = self.remove_before_entrance(mdf, odf, threshold, med)
        mdf, odf = self.remove_after_exit(mdf, odf, threshold, med)
        return mdf, odf
    
    
    # remove readings from ocean and motion dataframes where surfer is on land before entering the water
    def remove_before_entrance(self, mdf, odf, threshold, med):

        # get temperature series
        temps = odf['Calibrated Temperature 1']
        enter_index = self.get_water_entrance_index(temps, threshold, med)

        # get the time where the surfer enters the water in the ocean dataframe
        startTime = odf.iloc[enter_index]['Time']
        startTime /= 1000

        # find the index in motion dataframe that matches with start index calculated from ocean dataframe
        startIdx = mdf.iloc[(mdf['Time']-startTime).abs().argsort()[:1]]
        return mdf.loc[startIdx.index[0]:], odf.tail(len(odf) - enter_index)


    # calculate the index in ocean dataframe that the surfer enters the water
    def get_water_entrance_index(self, temps, threshold, med):

        above = False
        count = 0
        consecutiveWithin = 0

        # calculate the index at the point where the temperature readings fall within the threshold consecutively
        for time, reading in temps.items():
            if abs(reading - med) < threshold:
                if above == True:
                    above = False
                    firstInstance = count
                else:
                    consecutiveWithin += 1

                # if the temperatures fall within the threshold consecutively, then we can assume the surfer is in the water
                if consecutiveWithin > 10:
                    return count

                above = False

            else:
                above = True
                consecutiveWithin = 0
                firstInstance = 0
            count += 1 

        return firstInstance
    
    # remove readings from ocean and motion dataframes where surfer is on land after exiting the water
    def remove_after_exit(self, mdf, odf, threshold, med):
        
        # get the temperature series
        temps = odf['Calibrated Temperature 1']
#         print('temps: ', temps)
        # get the index where surfer exits the water
        exit_index = self.get_water_exit_index(temps, threshold, med)
#         print('exit index: ', exit_index)

        # get the time where the surfer enters the water in the ocean dataframe
        end_time = odf.iloc[exit_index]['Time']
        end_time /= 1000

        # find the index in motion dataframe that matches with end index calculated from ocean dataframe
        end_idx = mdf.iloc[(mdf['Time']-end_time).abs().argsort()[:1]]
        return mdf.loc[:end_idx.index[0]], odf.head(exit_index)


    # calculate the index in ocean dataframe that the surfer enters the water
    def get_water_exit_index(self, temps, threshold, med):
        above = False
        count = 0

        # calculate the index at the last point where the temperature readings transition from within to outside the threshold 
        for time, reading in temps.items():
            if abs(reading - med) > threshold:

                # record index where temperature transition from within to outside the threshold
                if above == False:
                    above = True
                    firstInstance = count

                above = True

            else:
                above = False
                firstInstance = -1
            count += 1 

        return firstInstance
    

    
    def get_timeframe(self, df):
        
        # get the times of the first and last reading
        df = df.reset_index()
        df = df.set_index('UTC')
        print('df length: ', len(df))

        start_time = df.index[0].timestamp()
        end_time = df.index[-1].timestamp()
        return start_time, end_time
    

        