from django.db import models

from constituents.models import Vote


class Bill(models.Model):
    state = models.CharField(max_length=2, choices=[('tn', 'Tennessee')])
    session = models.IntegerField()
    chamber = models.CharField(max_length=5, choices=[('upper', 'Senate'), ('lower', 'House')])
    bill_id = models.CharField(max_length=7)
    title = models.TextField()
    subjects = models.ManyToManyField('Subject')
    scraped_subjects = models.CharField(max_length=200, null=True)
    topics = models.CharField(max_length=200, null=True)
    sponsors = models.ManyToManyField('legislators.Legislator')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['state', 'session', 'bill_id'], name='bill')
        ]

    def get_actions(self):
        a = Action.objects.filter(
            state=self.state,
            session=self.session,
            bill_id=self.bill_id
        ).order_by('date')

        return a

    def count_votes(self, position):
        c = Vote.objects.filter(
            state=self.state,
            session=self.session,
            bill_id=self.bill_id,
            position=position
        ).count()

        return c


class Action(models.Model):
    state = models.CharField(max_length=2, choices=[('tn', 'Tennessee')])
    session = models.IntegerField()
    bill_id = models.CharField(max_length=7)
    action = models.TextField()
    actor = models.CharField(max_length=5, choices=[('upper', 'Senate'), ('lower', 'House')])
    date = models.DateTimeField()


class Subject(models.Model):
    subject = models.CharField(max_length=100)
