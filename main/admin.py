from django.contrib.gis import admin
from django.db.models import ExpressionWrapper, F
from .models import Zipcode, BlockGroup, Neighborhood, Listing

class ZipcodeAdmin(admin.OSMGeoAdmin):
    search_fields = ['geoid']

class BlockGroupAdmin(admin.OSMGeoAdmin):
    search_fields = ['geoid']

class NeighborhoodAdmin(admin.OSMGeoAdmin):
    search_fields = ['name']

class ListingAdmin(admin.OSMGeoAdmin):
    search_fields = [
        'neighborhood',
        'neighbourhood_cleansed',
        'name',
        'description'
    ]
    raw_id_fields = [
        'zipcode',
        'block_group',
        'neighborhood',
    ]

admin.site.register(Zipcode, ZipcodeAdmin)
admin.site.register(BlockGroup, BlockGroupAdmin)
admin.site.register(Neighborhood, NeighborhoodAdmin)
admin.site.register(Listing, ListingAdmin)
