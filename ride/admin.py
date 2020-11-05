from django.contrib import admin
from .models import RideData, Buoy, DataframeCSV

# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

# Register your models here.
admin.site.register(RideData)
admin.site.register(Buoy)
admin.site.register(DataframeCSV)
# admin.site.register(OceanData)
# admin.site.register(MotionData)