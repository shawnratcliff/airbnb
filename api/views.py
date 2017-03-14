from main.models import (
    Neighborhood,
    Zipcode,
    BlockGroup,
    Listing,
    Amenity,
    Crime
)
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework import mixins
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.db.models.functions import AsGeoJSON
from api.serializers import NeighborhoodSerializer, ListingListSerializer, ListingDetailSerializer, AmenitySerializer
from api.filters import get_filter_query, random_sample
from api.stats import get_stats
from api.predict import predict_price
from django.core.cache import cache

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
            filters = request.data['filters']
            queryset = self.get_queryset().filter(get_filter_query(filters))
            if 'max_sample_size' in filters.keys():
                queryset = random_sample(queryset, filters['max_sample_size'])
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get', 'post'])
    @csrf_exempt
    def stats(self, request):
        if 'filters' in request.data.keys():
            filters = request.data['filters']
            queryset = self.get_queryset().filter(get_filter_query(filters))
        else:
            queryset = self.get_queryset()
        return Response(get_stats(queryset))

class ListingViewSet(FilterableViewSet):
    list_queryset = cache.get_or_set(
        'listings_with_geojson',
        Listing.objects.annotate(geometry=AsGeoJSON('point')),
        None)
    list_serializer_class = ListingListSerializer
    detail_queryset = Listing.objects.all()
    detail_serializer_class = ListingDetailSerializer

class NeighborhoodViewSet(FilterableViewSet):
    list_queryset = cache.get_or_set(
        'neighborhoods_with_geojson',
        Neighborhood.objects.annotate(geometry=AsGeoJSON('mpoly'),
                                      center=AsGeoJSON('centroid')),
        None)
    detail_queryset = list_queryset
    list_serializer_class = NeighborhoodSerializer
    detail_serializer_class = NeighborhoodSerializer

class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer

class PredictPriceView(APIView):
    """
    View to get price prediction.

    """
    @csrf_exempt
    def post(self, request, format=None):
        if 'listing_attrs' in request.data:
            return Response(predict_price(request.data['listing_attrs']))
        else:
            return Response('Error: No listing attributes were submitted.')