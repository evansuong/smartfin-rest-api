# Smartfin Ride API

This api is built on top of the Django REST framework and can be used to fetch IMU and Ocean data captured by the Smartfin surfboard tool, analyzed and processed by UCSD's Engineers for Exploration Smartfin Research Team.


## Requirements
* python 3.8
* pythoon virtual environment (recommended) [(set up)](https://docs.python-guide.org/dev/virtualenvs/)
* Django (3.1) [(set up)](https://docs.djangoproject.com/en/3.1/intro/install/)
* Django REST Framework [(set up)](https://www.django-rest-framework.org/)


## Installation (recommended to do this in a virtual environment)
    pip install django
    pip install djangorestframework
    pip install -r requirements.txt
    
## Run
use the runserver commmand from manage.py to host the api on your local machine 
    
    python manage.py runserver


## Structure 
### API info endpoints
| Endpoint          | HTTP Method | Result                                             |
|-------------------|-------------|----------------------------------------------------|
| ride/             | GET         | Get list of api endpoints and functionaltiy        |
| ride/ride-list/   | GET         | Get list of ids of all rides currently in database |
| ride/ride-fields/ | GET         | Get list of ride's fields                          |

### Get ride data 
| Endpoint                                                        | HTTP Method | Result                                                                                                                                      |
|-----------------------------------------------------------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| ride/ride-get/<str:rideId>/                                     | GET/POST    | Get ride data by id, if ride is not in database create new entry                                                                            |
| ride/ride-delete/<str:rideId>/ | DELETE | Delete a ride entry by id |
| ride/field-get/<str:rideId>/<str:fields>/                       | GET         | Get specified fields of a ride data entry. Specify multiple fields by separating them with a ":" i.e. "heightSmartfin:startDate"            |
| ride/random/ride-get/<int:count>/                               | GET         | Get list of random ride datas, length of list specified by "count"                                                                          |
| ride/random/field-get/<int:count>/<str:fields>/                 | GET         | Get list of random ride data fields, length specified by "count". Specify multiple fields with ":" separation                               |
| ride/location/ride-get/<str:location>/                          | GET         | Get list of ride datas filtered by location. Location can be the name of the city or county the session took place                          |
| ride/location/field-get/<str:location>/<str:fields>/            | GET         | Get list of ride data fields filtered by location. Specify multiple fields with ":" separation                                              |
| ride/date/ride-get/<int:startDate>/<int:endDate>/               | GET         | Get list of ride datas that occured between the start and end date specified. Dates are formatted in unix time                              |
| ride/date/field-get/<int:startDate>/<int:endDate>/<str:fields>/ | GET         | Get list of ride datas that occured between the start and end date specified. Specify multiple fields with ":" separation. Unix time dates. |


### other functionality
| Endpoint                                   | HTTP Method | Result                                                                                                                        |
|--------------------------------------------|-------------|-------------------------------------------------------------------------------------------------------------------------------|
| get-dataframe/<str:rideId>/<str:datatype>/ | GET         | get a CSV file of a smartfin session's data. Datatype can be either 'motion' (IMU sensor data) or 'ocean' (ocean sensor data) |
| buoy-list/                                 | GET         | get list of all currently deployed CDIP buoys                                                                                 |


# Usage Examples
### fetching list of ride fields:

```python
import requests
response = requests.get('https://lit-sands-95859.herokuapp.com/ride/ride-fields/')
data = response.json()
```

#### data: 
    {'List all ride ids': '/ride-list/',
     'List ride fields': '/ride-fields/',
     'Get single ride': '/ride-get/<str:rideId>/',
     'Get random set of rides': '/many/ride-get/<int:count>/',
     'Filter rides by location': '/location/ride-get/<str:location>/',
     'Filter rides by date': '/date/ride-get/<str:startDate>/<str:endDate>/',
     'Get single ride attribute': 'field-get/<str:rideId>/<str:fields>/',
     'Get attributes of random set of rides': 'random/field-get/<int:count>/<str:fields>/',
     'Get attributes of rides filtered by location': 'location/field-get/<str:location>/<str:fields>/',
     'Get attributes of rides filtered by date': 'date/field-get/<str:startDate>/<str:endDate>/<str:fields>/',
     'Update heights of all rides in database': 'update-heights/',
     'Get list of active CDIP buoys': 'buoy-list/'}

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


### parsing motion and ocean CSV string into a pandas dataframe through BytesIO:
```python
from io import BytesIO
import pandas as pd

csv_str = BytesIO(data['motionData'])
dataframe = pd.read_csv(csv_str)
```
