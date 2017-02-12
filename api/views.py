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

from django.db.models import F, FloatField
from django.db.models.functions import Greatest, Cast
from django.contrib.gis.db.models.functions import AsGeoJSON
from api.serializers import NeighborhoodSerializer, ListingListSerializer, ListingDetailSerializer, AmenitySerializer
from api.filters import get_filter_query

class FilterableViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    A base viewset that provides 'retrieve' and 'list' actions.
    Supports filtering on 'list' actions via POST or GET methods.

    Also supports dual serializer classes for list and detail views.

    To use it, override the class and set the queryset, list_serializer_class, and detail_serializer_class
    attributes to match the model.
    """
    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        else:
            return self.detail_serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.list_queryset
        else:
            return self.detail_queryset

    @list_route(methods=['get', 'post'])
    @csrf_exempt
    def filter(self, request):
        if 'filters' in request.data.keys():
            queryset = self.get_queryset().filter(get_filter_query(request.data['filters']))
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

class ListingViewSet(FilterableViewSet):
    list_queryset = Listing.objects.annotate(geometry=AsGeoJSON('point'))
    list_serializer_class = ListingListSerializer
    detail_queryset = Listing.objects.all()
    detail_serializer_class = ListingDetailSerializer

class NeighborhoodViewSet(FilterableViewSet):
    list_queryset = Neighborhood.objects.annotate(geometry=AsGeoJSON('mpoly')) # Annotate geometry because we're using a different serializer
    detail_queryset = list_queryset
    list_serializer_class = NeighborhoodSerializer
    detail_serializer_class = NeighborhoodSerializer

class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer