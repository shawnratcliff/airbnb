from django.contrib.gis import admin
from django.db.models import ExpressionWrapper, F
from .models import Zipcode, BlockGroup, Tract, Neighborhood, Listing, Crime, Amenity, Review

class ZipcodeAdmin(admin.OSMGeoAdmin):
    search_fields = ['geoid']

class BlockGroupAdmin(admin.OSMGeoAdmin):
    search_fields = ['geoid']

class TractAdmin(admin.OSMGeoAdmin):
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
        'tract',
        'block_group',
        'neighborhood',
    ]

class CrimeAdmin(admin.OSMGeoAdmin):
    search_fields = [
        'report_number',
        'crime_code',
        'crime_code_desc',
        'address',
    ]
    raw_id_fields = [
        'zipcode',
        'block_group',
        'neighborhood'
    ]

class ReviewAdmin(admin.ModelAdmin):
    search_fields=[
        'date',
        'comments',
    ]
    raw_id_fields=[
        'listing',
    ]

admin.site.register(Zipcode, ZipcodeAdmin)
admin.site.register(Tract, TractAdmin)
admin.site.register(BlockGroup, BlockGroupAdmin)
admin.site.register(Neighborhood, NeighborhoodAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Amenity)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Crime, CrimeAdmin)
