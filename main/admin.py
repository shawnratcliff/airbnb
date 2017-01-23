from django.contrib.gis import admin
from .models import Neighborhood, Listing

admin.site.register(Neighborhood, admin.OSMGeoAdmin)
admin.site.register(Listing, admin.OSMGeoAdmin)
