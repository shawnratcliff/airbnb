from main.models import (
    Neighborhood,
    Zipcode,
    BlockGroup,
    Listing,
    Amenity,
    Crime
)
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework import mixins
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Count
from django.db.models import F, ExpressionWrapper, Value
import json
from django.contrib.gis.db.models.functions import AsGeoJSON
from api.serializers import NeighborhoodSerializer, ListingSerializer, AmenitySerializer
from api.filters import get_filter_query

class FilterableViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    A base viewset that provides 'retrieve' and 'list' actions.
    Supports filtering on 'list' actions via POST or GET methods.

    To use it, override the class and set the .queryset and .serializer_class attributes to match the model.
    """
    @list_route(methods=['get', 'post'])
    @csrf_exempt
    def filter(self, request):
        if 'filters' in request.data.keys():
            queryset = self.queryset.filter(get_filter_query(request.data['filters']))
        else:
            queryset = self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class ListingViewSet(FilterableViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class NeighborhoodViewSet(FilterableViewSet):
    queryset = Neighborhood.objects.annotate(geometry=AsGeoJSON('mpoly')) # Annotate geometry because we're using a different serializer
    serializer_class = NeighborhoodSerializer

class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer