from django.db import models


class Legislator(models.Model):
    legislator_id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=50)
    given_name = models.CharField(max_length=50)
    family_name = models.CharField(max_length=50)
    state = models.CharField(max_length=9, choices=[('Tennessee', 'Tennessee')])
    chamber = models.CharField(max_length=5, choices=[('upper', 'Senate'), ('lower', 'House')])
    district = models.IntegerField(null=True)
    party = models.CharField(max_length=10, choices=[('Democratic', 'Democratic'), ('Republican', 'Republican')])
    image = models.URLField(max_length=200)


class Vote(models.Model):
    state = models.CharField(max_length=9, choices=[('Tennessee', 'Tennessee')])
    bill_id = models.ManyToManyField('bills.Bill')
    legislator_id = models.ManyToManyField('Legislator')
    option = models.CharField(max_length=10, choices=[('No', 'no'), ('Present', 'not voting'), ('Yes', 'yes')])
