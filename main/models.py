from django.contrib.gis.db import models

class Zipcode(models.Model):
    zipcode = models.CharField(max_length=5, unique=True)
    area_land = models.BigIntegerField() # in m^2
    area_water = models.BigIntegerField() # in m^2
    mpoly = models.MultiPolygonField()
    def __str__(self):
        return self.zipcode

class BlockGroup(models.Model):
    geoid = models.CharField(max_length=12, unique=True)
    area_land = models.BigIntegerField() # in m^2
    area_water = models.BigIntegerField() # in m^2
    mpoly = models.MultiPolygonField()
    def __str__(self):
        return self.geoid

class Neighborhood(models.Model):
    name = models.CharField(max_length=512, unique=True)
    mpoly = models.MultiPolygonField()
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Listing(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField()
    point = models.PointField()
    listing_url = models.CharField(max_length=512)
    scrape_id = models.BigIntegerField()
    last_scraped = models.DateField()
    description = models.TextField()
    host_id = models.BigIntegerField()
    host_name = models.CharField(max_length=512)
    host_since = models.DateField()
    host_is_superhost = models.BooleanField()
    host_identity_verified = models.BooleanField()
    neighborhood = models.ForeignKey(Neighborhood, null=True)
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
    def __str__(self):
        return "%d %s ($%.2f)" %  (self.pk, self.name, self.price)
