# smartfin_ride_api
backend api code for smartfin webapp

# Smartfin Ride API

Rest API can be used to fetch IMU and Ocean data captured by the Smartfin surfboard tool, analyzed and processed by UCSD's Engineers for Exploration Smartfin Research Team. This API provides users the ability to post ride ids to our smartfin database to be processed by our data analysis methods that we have been cultivating this past summer and fall. 

The Ride API can deliver the following: 
* id of smartfin session
* location (city, county, state) of session
* start time of session
* end time of session
* significant wave height calculated by smartfin
* significant wave height reported by nearest CDIP buoy
* time series displacement data calcualted by smartfin
* time series temperature data calcualted by smartfin
* sample rate of smartfin IMU time series data
* sample rate of smartfin ocean time series  data
* calibrated ocean temperature read by smartfin
* ocean temperature reported by nearest CDIP buoy
* nearest CDIP buoy to smartfin session
* latitude of smartfin session
* longitude of smartfin session
* IMU data csv string
* ocean sensor csv string

## Querying Ride Database:
use "https://" protocol to request data

pathway endpoints all begin from the API domain name: "lit-sands-95859.herokuapp.com/ride/"
the base endpoint returns the rest of the endpoints for the API

### from this append any of the api endpoints:
full ride data:
* "ride-list/": list of all ride ID's currently in the database
* "ride-fields/": list of all data fields for each database entry
* "ride-get/{rideId}/": returns the entry with the specified ride id, and creates a new entry if that ride is not found in the database
* "random/ride-get/{count}/": returns a random list of rides, the length of which is specified by "count"
* "location/ride-get/{location}/": filters rides in database by location (city) and returns the resulting entries
* "date/ride-get/{startDate}/{endDate}/": filters rides in database between the start and end dates (unix timestamps) and returns the resulting entries

query for specified field values:
* "field-get/{rideId}/{fields}/": returns the specified data fields of ride by ride id
* "random/field-get/{count}/{fields}/": returns a random list of specified data fields, the length of which is specified by "count" 
* "location/field-get/{location}/{fields}/": returns a list of specified data fields filtered by location (city)
* "date/field-get/{startDate}/{endDate}/{fields}/": returns a list of specified data fields filtered by start and end date (unix timestamps)\

NOTE: you can query for multiple data fields at a time, separating each field with a colon: "field1:field2:field3:..."
NOTE: all data is returned in JSON format


# Usage Examples
### fetching list of ride fields:

```python
import requests
response = requests.get('https://lit-sands-95859.herokuapp.com/ride/ride-fields/')
data = response.json()
```

data: 
{'id of smartfin session': 'rideId',
 'location (city, county, state) of session': 'loc1, loc2, loc3',
 'start time of session': 'startTime',
 'end time of session': 'endTime',
 'significant wave height calculated by smartfin': 'heightSmartfin',
 'significant wave height reported by nearest CDIP buoy': 'heightCDIP',
 'time series displacement data calcualted by smartfin': 'heightList',
 'time series temperature data calcualted by smartfin': 'tempList',
 'sample rate of smartfin IMU time series data': 'heightSampleRate',
 'sample rate of smartfin ocean time series  data': 'tempSampleRate',
 'calibrated ocean temperature read by smartfin': 'tempSmartfin',
 'ocean temperature reported by nearest CDIP buoy': 'tempCDIP',
 'nearest CDIP buoy to smartfin session': 'buoyCDIP',
 'latitude of smartfin session': 'latitude',
 'longitude of smartfin session': 'longitude',
 'IMU data csv file': 'motionData',
 'ocean sensor csv file': 'oceanData'}

### fetching all rides in san diego
```python
import requests
response = requests.get('https://lit-sands-95859.herokuapp.com/ride/location/ride-get/{location}/')
data = response.json()
```

### fetching 5 heights and temperatures of smartfin rides randomly
```python
import requests
response = requests.get('https://lit-sands-95859.herokuapp.com/ride/random/field-get/5/heightSmartfin:tempSmartfin/')
data = response.json()
```
data: 
[{'rideId': '16135',
  'heightSmartfin': 0.39656736009880406,
  'tempSmartfin': 19.571597727272728},
 {'rideId': '16168',
  'heightSmartfin': 0.5290967091550641,
  'tempSmartfin': 18.534223706176963},
 {'rideId': '15962',
  'heightSmartfin': 0.4584329574188188,
  'tempSmartfin': 15.612076023391813},
 {'rideId': '16178',
  'heightSmartfin': 0.4679436020698194,
  'tempSmartfin': 18.86951451187335},
 {'rideId': '16380',
  'heightSmartfin': 0.5590487240759578,
  'tempSmartfin': 17.33151226158038}]


### parsing motion and ocean CSV string into a pandas dataframe through StringIO:
from io import StringIO
import pandas as pd

csv_str = StringIO(data['motionData'])
dataframe = pd.read_csv(csv_str)
