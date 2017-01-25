from django.contrib.gis import admin
from .models import Zipcode, BlockGroup, Neighborhood, Listing

class ZipcodeAdmin(admin.OSMGeoAdmin):
    search_fields = ['zipcode']

class BlockGroupAdmin(admin.OSMGeoAdmin):
    search_fields = ['geoid']

class NeighborhoodAdmin(admin.OSMGeoAdmin):
    search_fields = ['name']

class ListingAdmin(admin.OSMGeoAdmin):
    search_fields = ['neighborhood', 'neighbourhood_cleansed', 'name', 'description']

admin.site.register(Zipcode, ZipcodeAdmin)
admin.site.register(BlockGroup, BlockGroupAdmin)
admin.site.register(Neighborhood, NeighborhoodAdmin)
admin.site.register(Listing, ListingAdmin)
