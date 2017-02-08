from main.models import (
    Neighborhood,
    Zipcode,
    BlockGroup,
    Listing,
    Amenity,
    Crime
)
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

class NeighborhoodSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Neighborhood
        geo_field = 'mpoly'
        fields = ('id', 'name', 'data')

class ZipcodeSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Zipcode
        geo_field = 'mpoly'
        fields = ('id', 'geoid', 'data')

class BlockGroupSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = BlockGroup
        geo_field = 'mpoly'
        fields = ('id', 'geoid', 'data')

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Amenity
        fields=('id', 'name')

class ListingSerializer(gis_serializers.GeoFeatureModelSerializer):
    estimated_monthly_revenue = serializers.DecimalField(max_digits=9,
                                                         decimal_places=2)
    amenities = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        geo_field = 'point'
        fields = ('id', 'name', 'neighborhood', 'description', 'price',
                  'property_type', 'room_type', 'bed_type',
                  'estimated_monthly_revenue', 'accommodates', 'amenities')

    def get_amenities(self, obj):
        return [amenity.name for amenity in obj.amenities.all()]