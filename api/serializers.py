from main.models import (
    Neighborhood,
    Zipcode,
    BlockGroup,
    Listing,
    Crime
)
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

class NeighborhoodSerializer(gis_serializers.GeoFeatureModelSerializer):
    crime_count = serializers.IntegerField()
    class Meta:
        model = Neighborhood
        geo_field = 'mpoly'
        fields = ('name', 'crime_count')

class ListingSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Listing
        geo_field = 'point'
        fields = ('id', 'name', 'neighborhood', 'description', 'price')