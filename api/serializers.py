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
from collections import OrderedDict
from rest_framework.serializers import ListSerializer
import json

"""
Quick and dirty serializers to replace the inefficient ones in the DRF GIS library.
Careful, these aren't safe for relational fields.
"""

class FastGeoJSONListSerializer(ListSerializer):
    @property
    def data(self):
        return super(ListSerializer, self).data

    def to_representation(self, data):
        """
        Add GeoJSON compatible formatting to a serialized queryset list
        """
        return OrderedDict((
            ("type", "FeatureCollection"),
            ("features", super(FastGeoJSONListSerializer, self).to_representation(data))
        ))


class FastGeoJSONSerializer(serializers.BaseSerializer):
    geometry = serializers.JSONField()
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'type': 'Feature',
            'geometry': json.loads(obj.geometry),
            'properties': {
                field_name: getattr(obj, field_name)
                for field_name in self.property_fields
            }
        }
    class Meta:
        list_serializer_class = FastGeoJSONListSerializer

class NeighborhoodSerializer(FastGeoJSONSerializer):
    property_fields = ('name', 'data')

class ZipcodeSerializer(FastGeoJSONSerializer):
    property_fields = ('geoid', 'data')

class BlockGroupSerializer(FastGeoJSONSerializer):
    property_fields = ('geoid', 'data')

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
        return [amenity['name'] for amenity in obj.amenities.values('name')]
