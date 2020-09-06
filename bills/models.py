from django.db import models

from constituents.models import Vote


class Bill(models.Model):
    bill_id = models.CharField(max_length=45, primary_key=True)
    state = models.CharField(max_length=9, choices=[('Tennessee', 'Tennessee')])
    session = models.IntegerField()
    chamber = models.CharField(max_length=5, choices=[('upper', 'Senate'), ('lower', 'House')])
    name = models.CharField(max_length=7)
    title = models.TextField()
    scraped_subjects = models.CharField(max_length=200, null=True)
    subjects = models.ManyToManyField('Subject')
    topics = models.ManyToManyField('Topic')
    sponsors = models.ManyToManyField('legislators.Legislator')
    companion_name = models.CharField(max_length=7)

    def get_actions(self):
        a = Action.objects.filter(
            state=self.state,
            session=self.session,
            name=self.name
        ).order_by('date')

        return a

    def count_votes(self, position):
        c = Vote.objects.filter(
            state=self.state,
            session=self.session,
            name=self.name,
            position=position
        ).count()

        return c


class Action(models.Model):
    bill_id = models.ForeignKey('Bill', on_delete=models.CASCADE)
    state = models.CharField(max_length=9, choices=[('Tennessee', 'Tennessee')])
    session = models.IntegerField()
    name = models.CharField(max_length=7)
    action = models.CharField(max_length=256)
    actor = models.CharField(
        max_length=53,
        choices=[
            ('ocd-organization/47760e16-8071-49dd-bd9f-354198c8b653', 'Senate'),
            ('ocd-organization/d4c442c8-d4d7-4ea9-a3fd-b856b2904d8b', 'House')
        ]
    )
    classification = models.CharField(max_length=32)
    date = models.DateTimeField()


class Subject(models.Model):
    subject = models.CharField(max_length=100)


class Topic(models.Model):
    topic = models.CharField(max_length=100)
