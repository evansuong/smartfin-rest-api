from django.db import models

# Create your models here.
class RideData(models.Model):

    rideId = models.CharField(max_length=5, primary_key=True) 

    # ride location by city
    loc1 = models.CharField(max_length=50, blank=True, null=True)
    loc2 = models.CharField(max_length=50, blank=True, null=True)
    loc3 = models.CharField(max_length=50, blank=True, null=True)

    # start and end times in Unix time 
    startTime = models.IntegerField(blank=True, null=True)
    endTime = models.IntegerField(blank=True, null=True)

    # smartfin calculated data
    heightSmartfin = models.FloatField(blank=True, null=True)
    tempSmartfin = models.FloatField(blank=True, null=True)

    # CDIP calculated data
    buoyCDIP = models.CharField(max_length=3, blank=True, null=True)
    heightCDIP = models.FloatField(blank=True, null=True)
    tempCDIP = models.FloatField(blank=True, null=True)

    # ride location
    latitude = models.FloatField(max_length=10, blank=True, null=True)
    longitude = models.FloatField(max_length=10, blank=True, null=True)


    def __str__(self):
        return f'ride {self.rideId}'


class DataframeCSV(models.Model): 
    ride = models.ForeignKey(RideData, on_delete=models.CASCADE)
    filePath = models.CharField(max_length=50, blank=True, null=True)
    datatype = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f'{self.filePath}'

# list of all active CDIP buoys
class Buoy(models.Model):

    buoyNum = models.CharField(max_length=3, primary_key=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'buoy {self.buoyNum}'
