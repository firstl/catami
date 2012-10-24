__author__ = 'mat'

from django.contrib import admin
from Force.models import *
from django.contrib.gis import admin 

class AUVDeploymentAdmin(admin.ModelAdmin):
	list_display = ('start_time_stamp','end_time_stamp','distance_covered','min_depth','max_depth','mission_aim')

#admin.site.register(AUVDeployment, AUVDeploymentAdmin)
#admin.site.register(Campaign)
admin.site.register(AUVDeployment, admin.GeoModelAdmin)
admin.site.register(BRUVDeployment, admin.GeoModelAdmin)
admin.site.register(DOVDeployment, admin.GeoModelAdmin)
admin.site.register(Campaign, admin.GeoModelAdmin)


