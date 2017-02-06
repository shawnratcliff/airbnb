from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models import Avg

class Zipcode(models.Model):
    geoid = models.CharField(max_length=5)
    land_area = models.FloatField() # in m^2
    water_area = models.FloatField() # in m^2
    mpoly = models.MultiPolygonField(spatial_index=True)
    fixed_data = JSONField(default=dict)
    def __str__(self):
        return self.zipcode
    @property
    def zipcode(self):
        return self.geoid

class BlockGroup(models.Model):
    geoid = models.CharField(max_length=12)
    land_area = models.FloatField() # in m^2
    water_area = models.FloatField() # in m^2
    mpoly = models.MultiPolygonField(spatial_index=True)
    fixed_data = JSONField(default=dict)
    def __str__(self):
        return self.geoid

class Neighborhood(models.Model):
    name = models.CharField(max_length=512, unique=True)
    mpoly = models.MultiPolygonField(spatial_index=True)
    fixed_data = JSONField(default=dict)
    computed_stats = JSONField(default=dict)
    def __str__(self):
        return self.name
    @property
    def data(self):
        """Return one object containing both fixed data and computed statistics."""
        return {**self.fixed_data, **self.computed_stats} # Merges dicts. (See PEP 478 re: syntax.)
    def update_stats(self):
        """ Update computed_stats field """
        self.computed_stats = {
            'crime_count': self.crime_set.count(),
            'listing_count': self.listing_set.count(),
            'avg_listing_price': self.listing_set.aggregate(Avg('price'))['price__avg'],
        }
        self.save()

class Crime(models.Model):
    # Geo fields
    neighborhood = models.ForeignKey(Neighborhood, db_index=True, null=True)
    zipcode = models.ForeignKey(Zipcode, db_index=True, null=True)
    block_group = models.ForeignKey(BlockGroup, db_index=True, null=True)
    point = models.PointField(spatial_index=True)

    report_number = models.BigIntegerField() # NOT UNIQUE
    date_reported = models.DateField()
    date_occurred = models.DateTimeField()
    crime_code = models.IntegerField()
    crime_code_desc = models.TextField(max_length=512)
    def __str__(self):
        neighborhood_name = self.neighborhood.name if self.neighborhood else ""
        zipcode_digits = self.zipcode.geoid if self.zipcode else ""
        return "%s (%s %s) %s" % (
            self.crime_code_desc,
            neighborhood_name,
            zipcode_digits,
            self.report_number
        )

class Listing(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField()
    # Geo fields
    neighborhood = models.ForeignKey(Neighborhood, db_index=True, null=True)
    zipcode = models.ForeignKey(Zipcode, db_index=True, null=True)
    block_group = models.ForeignKey(BlockGroup, db_index=True, null=True)
    point = models.PointField(spatial_index=True)
    # Data fields
    listing_url = models.CharField(max_length=512)
    scrape_id = models.BigIntegerField()
    last_scraped = models.DateField()
    description = models.TextField()
    host_id = models.BigIntegerField()
    host_name = models.CharField(max_length=512)
    host_since = models.DateField()
    host_is_superhost = models.BooleanField()
    host_identity_verified = models.BooleanField()
    neighbourhood_cleansed = models.CharField(max_length=512)
    property_type = models.CharField(max_length=512)
    room_type = models.CharField(max_length=512)
    accommodates = models.IntegerField()
    bathrooms = models.FloatField() # CHECK FOR NAN
    bedrooms = models.FloatField() # CHECK FOR NAN
    bed_type = models.CharField(max_length=512)
    amenities = models.TextField()
    price = models.FloatField()
    minimum_nights = models.IntegerField()
    availability_365 = models.IntegerField()
    number_of_reviews = models.IntegerField()
    reviews_per_month = models.FloatField()
    street = models.CharField(max_length=512)
    @property
    def estimated_monthly_revenue(self):
        # Using InsideAirbnb "San Francisco Model":
        # Bookings = 2 * reviews per month
        # Length of stay = max(min_nights, 4.5 nights [LA market average])
        # All multiplied by price
        # (LA average stay source: https://los-angeles.airbnbcitizen.com/airbnb-home-sharing-activity-report-los-angeles/)
        return (self.price
                * max(4.5, self.minimum_nights)
                * 2
                * self.reviews_per_month)

    def __str__(self):
        return "%s %s ($%.2f)" %  (self.pk, self.name, self.price)
