from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models import Avg, Sum, F, FloatField
from django.db.models.functions import Cast, Greatest
from pg_utils import Seconds
from random import randint

SECONDS_PER_YEAR = 3.154e+7

def rand_num():
    return randint(0, 100000000)

class Neighborhood(models.Model):
    name = models.CharField(max_length=512, unique=True)
    mpoly = models.MultiPolygonField(spatial_index=True)
    centroid = models.PointField(null=True)
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
        num_listings = self.listing_set.count()
        avg_listing_price = self.listing_set.aggregate(Avg('price'))['price__avg']
        avg_estimated_bookings_per_listing_per_month = (
            None if num_listings == 0
            else 2.0 * self.listing_set.aggregate(Avg('reviews_per_month'))['reviews_per_month__avg']
        )
        self.computed_stats = {
            'crime_count': self.crime_set.count(),
            'listing_count': self.listing_set.count(),
            'avg_listing_price': avg_listing_price,
            'avg_estimated_bookings_per_listing_per_month': avg_estimated_bookings_per_listing_per_month,
            'avg_estimated_revenue_per_listing_per_month': (
                None if num_listings == 0
                else self.listing_set.aggregate(Avg('estimated_revenue_per_month'))['estimated_revenue_per_month__avg']
            ),
            'total_estimated_bookings_per_month':(
                0 if num_listings == 0
                else self.listing_set.aggregate(Sum('reviews_per_month'), )['reviews_per_month__sum']
            ),
            'avg_host_experience_years': self.listing_set.aggregate(
                avg_host_exp=Avg(Seconds(F('last_scraped') - F('host_since'))) / SECONDS_PER_YEAR)['avg_host_exp'],
        }
        self.save()

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
    centroid = models.PointField(null=True)
    neighborhood = models.ForeignKey(Neighborhood, null=True)
    fixed_data = JSONField(default=dict)
    def __str__(self):
        return self.geoid

class Tract(models.Model):
    geoid = models.CharField(max_length=12)
    land_area = models.FloatField() # in m^2
    water_area = models.FloatField() # in m^2
    mpoly = models.MultiPolygonField(spatial_index=True)
    centroid = models.PointField(null=True)
    neighborhood = models.ForeignKey(Neighborhood, null=True)
    fixed_data = JSONField(default=dict)
    def __str__(self):
        return self.geoid

class Crime(models.Model):
    # Geo fields
    neighborhood = models.ForeignKey(Neighborhood, db_index=True, null=True)
    zipcode = models.ForeignKey(Zipcode, db_index=True, null=True)
    block_group = models.ForeignKey(BlockGroup, db_index=True, null=True)
    point = models.PointField(spatial_index=True)

    data_source = models.CharField(
        max_length=16,
        db_index=True,
        null=False,
        choices=(('LAPD', 'Los Angeles Police Department'), ('LACS', 'Los Angeles County Sheriff'))
    )
    report_number = models.BigIntegerField() # NOT UNIQUE
    date_reported = models.DateField()
    date_occurred = models.DateTimeField()
    category = models.CharField(max_length=512, null=True)
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

class Amenity(models.Model):
    name = models.CharField(max_length=128, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering=('name',)
        verbose_name_plural='amenities'

class Listing(models.Model):
    id = models.BigIntegerField(primary_key=True)
    random = models.IntegerField(default=rand_num, db_index=True) # Random num for fast shuffling
    name = models.TextField()
    # Geo fields
    neighborhood = models.ForeignKey(Neighborhood, db_index=True, null=True)
    zipcode = models.ForeignKey(Zipcode, db_index=True, null=True)
    tract = models.ForeignKey(Tract, db_index=True, null=True)
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
    amenities = models.ManyToManyField(Amenity)
    raw_amenities = models.TextField()
    price = models.FloatField()
    minimum_nights = models.IntegerField()
    availability_365 = models.IntegerField()
    number_of_reviews = models.IntegerField()
    reviews_per_month = models.FloatField()
    street = models.CharField(max_length=512)
    estimated_revenue_per_month = models.FloatField(default=0)

    def update_stats(self):
        # Using InsideAirbnb "San Francisco Model":
        # Bookings = 2 * reviews per month
        # Length of stay = max(min_nights, 4.5 nights [LA market average])
        # Subtotal: estimated occupancy days per month. Cap at 70% (21 days total)
        # Multiply by nightly price
        # (LA average stay source: https://los-angeles.airbnbcitizen.com/airbnb-home-sharing-activity-report-los-angeles/)
        num_bookings = 2 * self.reviews_per_month
        days_occupied = min(21, num_bookings * max(4.5, self.minimum_nights))
        self.estimated_revenue_per_month = self.price * days_occupied
        self.save()

    def __str__(self):
        return "%s %s ($%.2f)" %  (self.pk, self.name, self.price)

class Review(models.Model):
    id = models.BigIntegerField(primary_key=True)
    listing = models.ForeignKey(Listing)
    date = models.DateField()
    reviewer_id = models.BigIntegerField()
    comments = models.TextField(null=True)
    def __str__(self):
        return ("%s %s %s" % (self.listing_id, self.date, self.comments[:50] ))


