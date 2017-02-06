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
    class Meta:
        model = Neighborhood
        geo_field = 'mpoly'
        fields = ('name', 'data')

class ListingSerializer(gis_serializers.GeoFeatureModelSerializer):
    estimated_monthly_revenue = serializers.DecimalField(max_digits=9,
                                                         decimal_places=2)
    class Meta:
        model = Listing
        geo_field = 'point'
        fields = ('id', 'name', 'neighborhood', 'description', 'price',
                  'property_type', 'room_type', 'bed_type',
                  'estimated_monthly_revenue', 'accommodates')