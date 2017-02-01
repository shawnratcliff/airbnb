from main.models import (
    Neighborhood,
    Zipcode,
    BlockGroup,
    Listing,
    Crime
)
from rest_framework import viewsets
from api.serializers import NeighborhoodSerializer, ListingSerializer
from django.db.models import Count

class NeighborhoodViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Neighborhood.objects.annotate(
        crime_count=Count('crime')).order_by('name')
    serializer_class = NeighborhoodSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer