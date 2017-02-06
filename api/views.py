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
from django.db.models import F, ExpressionWrapper, Value

class NeighborhoodViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()

    # TEMPORARY: RESTRICT LIST TO SANTA MONICA ONLY
    #queryset = Listing.objects.filter(
    #    neighborhood=Neighborhood.objects.get(name="Santa Monica"))

    serializer_class = ListingSerializer