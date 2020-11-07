from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Q
from rest_framework import serializers

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import RideSerializer, HeightSerializer, TempSerializer, BuoySerializer

from .modules.smartfin_ride_module import RideModule
from .models import RideData, Buoy, DataframeCSV
import json
import random
import sys
from zipfile import ZipFile
from wsgiref.util import FileWrapper




# TODO: combine get many with the location and date views


# Create your views here.
@api_view(['GET'])
def rideOverview(request):
    # list of url patterns in this api
    api_urls = {
        'List all ride ids': '/ride-list/',
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
        'Get list of active CDIP buoys': 'buoy-list/'
    }

    return Response(api_urls)



# get list of all rideIds
@api_view(['GET'])
def rideList(request):
    rd = RideData.objects.all()
    data = rd.values_list('rideId', flat=True).order_by('startTime')
    data = {'ids': list(data)}
    return JsonResponse(data)



@api_view(['GET'])
def rideFields(request):
    data = {
        'id of smartfin session': 'rideId',
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
        'ocean sensor csv file': 'oceanData'
    }
    return JsonResponse(data)



# create new ride or return it if it is already in the database 
@api_view(['GET'])
def rideGet(request, rideId):
    # if ride already exists in the database, return it
    try: 
        data = RideData.objects.get(rideId=rideId)
        print('found ride in database, returning data...')

    # if ride doesn't exist, then create a new model and fill its data
    except:
        rideModule = RideModule()

        # get all CDIP buoys from db
        buoys = Buoy.objects.values()
        if len(buoys) == 0:
            buoys = rideModule.get_CDIP_stations()
            for buoy in buoys:
                buoyModel = Buoy(**buoy)
                buoyModel.save()
    
        # fetch data from the ride_module
        data, dfs = rideModule.get_ride_data(rideId, buoys)
        print(data)
        if data == {}:
            return JsonResponse({"Error": f"no such ride '{rideId}' exists"})

        # save ride data into RideData model
        rideModel = RideData(**data)
        rideModel.save()

        mdfModel = DataframeCSV(ride=rideModel, filePath=dfs['motionData'], datatype='motion')
        mdfModel.save()
        odfModel = DataframeCSV(ride=rideModel, filePath=dfs['oceanData'], datatype='ocean')
        odfModel.save()
        print(f'uploaded {sys.getsizeof(data)} bytes of ride data to database...')

    # return ride data that was sent to model
    serializer = RideSerializer(data, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def rideGetRandom(request, count):

    rideSet = RideData.objects.all()
        
    if count > 0:
        if count > len(rideSet):
            if len(rideSet) == 1:
                return JsonResponse({ "Error": f"there is only {len(rideSet)} entry currently in the database" })
            else:
                return JsonResponse({ "Error": f"there are only {len(rideSet)} entries currently in the database" })

        rideSet = RideData.objects.all()
        rideSet = random.sample(list(rideSet), count)
    serializer = RideSerializer(rideSet, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def rideGetLocation(request, location):
    # return all ride ids if all locations are specified
    if (location == 'all'):
        rideSet = RideData.objects.all()
    # only return ids in the specified location
    else:
        if ':' in location:
            loc1, loc3 = location.split(':')
        else:
            loc1 = location
            loc3 = location
        # here | is being used as set union not bitwise OR
        rideSet = RideData.objects.filter(Q(loc1=loc1) | Q(loc2=loc1) | Q(loc3=loc1) | Q(loc1=loc3) | Q(loc2=loc3) | Q(loc3=loc3))

    if len(rideSet) <= 0:
        return JsonResponse({ "Error": "no rides found in this location" })

    serializer = RideSerializer(rideSet, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def rideGetDate(request, startDate, endDate):
    
    if startDate == 'all':
        rideSet = RideData.objects.all
    try:     
        startDate = int(startDate)
        endDate = int(endDate)
        if startDate > endDate:
            return JsonResponse({"Error": "end date must be greater than start date"})
    except:
        return JsonResponse({'Error': 'dates must be formatted in unix time'})

    # get all rides that occur after the startDate
    rideSet = RideData.objects.filter(Q(startTime__gte=startDate) & Q(endTime__lte=endDate))
    if len(rideSet) <= 0:
        return JsonResponse({ "Error": f"No rides found between {startDate} and {endDate}" })

    serializer = RideSerializer(rideSet, many=True)
    return Response(serializer.data)


# get single field from ride
@api_view(['GET']) 
def fieldGet(request, rideId, fields):

    # parse attributes
    attributes = []
    if ':' in fields:
        attributes = fields.split(':')
    else:
        attributes.append(fields)
 
    data = {}
    try:
        field = RideData.objects.get(rideId=rideId)
    except:
        return JsonResponse({"Error": f"No such ride {rideId} found in database, create a new ride if the ride should exist with the ride-get query"})

    for attribute in attributes:
        data[attribute] = getattr(field, attribute)


    return JsonResponse(data)


# get single field from multiple random rides
@api_view(['GET'])
def fieldGetRandom(request, fields, count):

    # parse attributes 
    if 'rideId' not in fields:
        fields = 'rideId:' + fields
    attributes = []
    if ':' in fields:
        attributes = fields.split(':')
    else:
        attributes.append(fields)

    # build set if ride attributes
    fieldSet = RideData.objects.all().values_list(*attributes)
    if count > 0:
         if count > len(fieldSet):
            if len(fieldSet) == 1:
                return JsonResponse({ "Error": f"there is only {len(fieldSet)} entry currently in the database" })
            else:
                return JsonResponse({ "Error": f"there are only {len(fieldSet)} entries currently in the database" })
        
    fieldSet = random.sample(list(fieldSet), count)

    # format data to send back
    data = {'data': [dict(zip(attributes, values)) for values in fieldSet]}
    return JsonResponse(data)


@api_view(['GET'])
def fieldGetLocation(request, fields, location):

    # parse attributes
    attributes = []
    if ':' in fields:
        attributes = fields.split(':')

    else:
        attributes.append(fields)

    # return all ride ids if all locations are specified
    if (location == 'all'):
        fieldSet = RideData.objects.all()
        fieldSet = fieldSet.values_list(*attributes)
    # only return ids in the specified location
    else:
        if ':' in location:
            loc1, loc3 = location.split(':')
        else:
            loc1 = location
            loc3 = location
        # here | is being used as set union not bitwise OR
        fieldSet = RideData.objects.filter(Q(loc1=loc1) | Q(loc2=loc1) | Q(loc3=loc1) | Q(loc1=loc3) | Q(loc2=loc3) | Q(loc3=loc3))
        fieldSet = fieldSet.values_list(*attributes)

    if len(fieldSet) <= 0:
        return JsonResponse({ "Error": "no rides found in this location" })
    
    data = {'data': [dict(zip(attributes, values)) for values in fieldSet]}
    return JsonResponse(data)


@api_view(['GET'])
def fieldGetDate(request, startDate, endDate, fields):
    
     # parse attributes
    attributes = []
    if ':' in fields:
        attributes = fields.split(':')

    else:
        attributes.append(fields)

    # parse dates
    try:     
        startDate = int(startDate)
        endDate = int(endDate)
       
        if startDate > endDate:
            return JsonResponse({"Error": "end date must be greater than start date"})
  
    except:
        return JsonResponse({'error': 'dates must be formatted in unix time'})

    # get all rides that occur after the startDate and before end date
    fieldSet = RideData.objects.filter(Q(startTime__gte=startDate) & Q(endTime__lte=endDate))
    fieldSet = fieldSet.values_list(*attributes)

    if len(fieldSet) <= 0:
        return JsonResponse({ "Error": f"No rides found between {startDate} and {endDate}" })

    data = {'data': [dict(zip(attributes, values)) for values in fieldSet]}
    return JsonResponse(data)





@api_view(['PUT'])
# used to update smartfin calculated heights when new analysis method is used
def updateHeights(request):

    # get all ids currently in database
    ids = RideData.objects.values_list('rideId', flat=True)
    rm = RideModule()

    # for each ride currently in database...
    for id in ids:
        rd = RideData.objects.get(rideId=id)
        mdf = getattr(rd, 'motionData')
        # calculate the new ride height from updated height analysis algorithm
        heightUpdated = rm.get_ride_height(id, mdf)

        # update the old height in the database
        ride = RideData.objects.get(rideId=id)
        ride.heightSmartfin = heightUpdated  # change field
        ride.save() # this will update only

    return JsonResponse({'success': 'rides updated '})


@api_view(['GET'])
def get_dataframe(response, rideId, datatype, download=False):

    try:
        dfPath = DataframeCSV.objects.get(ride__rideId=rideId, datatype=datatype)
    except:
        return JsonResponse({"Error": f"No such ride {rideId} found in database, create a new ride if the ride should exist with the ride-get query"})
    dfPath = getattr(dfPath, 'filePath')
    print(dfPath)
    fi = open(dfPath, 'rb')
    return FileResponse(fi)




@api_view(['GET'])
def buoyList(request):
    
    # return list of buoys
    data = Buoy.objects.all().values_list('buoyNum', flat=True)
    print(data)
    return Response(data)


