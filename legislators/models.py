from django.db import models


# TODO: All leg_id are missing in OS data
class Legislator(models.Model):
    leg_id = models.CharField(max_length=16)
    full_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    suffix = models.CharField(max_length=50)
    active = models.BooleanField()
    state = models.CharField(max_length=2)
    chamber = models.CharField(max_length=5, choices=[('upper', 'Senate'), ('lower', 'House')])
    district = models.IntegerField(null=True)
    party = models.CharField(max_length=10, choices=[('Democratic', 'Democratic'), ('Republican', 'Republican')])
    photo_url = models.CharField(max_length=200)
