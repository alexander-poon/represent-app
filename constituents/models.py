from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from geopy.geocoders import Nominatim
from pyopenstates import locate_legislators


class Constituent(AbstractUser):
	constituent_id = models.AutoField(primary_key=True)
	address = models.CharField(max_length=256, null=True)
	city = models.CharField(max_length=32, null=True)
	county = models.CharField(max_length=32, null=True)
	rep = models.CharField(max_length=8, null=True)
	senator = models.CharField(max_length=8, null=True)

	class Meta:
		verbose_name = 'Constituent'
		verbose_name_plural = 'Constituents'

	def __str__(self):
		return self.username

	def save(self, *args, **kwargs):

		if self.address:
			geocoder = Nominatim(user_agent='represent')
			g = geocoder.geocode(self.address, country_codes='us', addressdetails=True)

			lat, long = [g.raw.get(i) for i in ['lat', 'lon']]
			city = g.raw.get('address').get('city')
			county = g.raw.get('address').get('county')
			self.city = city
			self.county = county

			legislators = locate_legislators(lat=lat, long=long)
			self.rep = [i.get('leg_id') for i in legislators if i.get('chamber') == 'lower'][0]
			self.senator = [i.get('leg_id') for i in legislators if i.get('chamber') == 'upper'][0]

		super().save(*args, **kwargs)


class Vote(models.Model):
	constituent = models.ForeignKey('Constituent', on_delete=models.CASCADE)
	state = models.CharField(max_length=2, choices=[('tn', 'Tennessee')])
	session = models.IntegerField()
	bill_id = models.CharField(max_length=7)
	position = models.CharField(
		max_length=11,
		choices=[('support', 'Support'), ('oppose', 'Oppose'), ('indifferent', 'Indifferent'), ('', '')],
		default=''
	)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['constituent_id', 'state', 'session', 'bill_id'],
				name='constituent_vote'
			)
		]
