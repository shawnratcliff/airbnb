from django.contrib.gis.db import models

class Neighborhood(models.Model):
    name = models.CharField(max_length=128, unique=True)
    mpoly = models.MultiPolygonField()
    def __str__(self):
        return self.name



