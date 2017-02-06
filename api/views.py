from main.models import (
    Neighborhood,
    Zipcode,
    BlockGroup,
    Listing,
    Crime
)
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.db.models import Count
from django.db.models import F, ExpressionWrapper, Value
import json

from api.serializers import NeighborhoodSerializer, ListingSerializer
from api.filters import get_filter_query


class NeighborhoodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer


class ListingViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving Airbnb listings
    """

    def list(self, request):
        if 'filters' in request.data.keys():
            queryset = Listing.objects.filter(get_filter_query(request.data['filters']))
        else:
            queryset = Listing.objects.filter(price__gte=3000.0)
        serializer = ListingSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        listing = get_object_or_404(queryset, pk=pk)
        serializer = ListingSerializer(listing)
        return Response(serializer.data)