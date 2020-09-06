import pandas as pd
from django.db import migrations


def create_legislator_votes(apps, schema_editor):
    vote_events = pd.read_csv('represent/tn_111/TN/111/TN_111_votes.csv') \
        .query('motion_text.str.contains("PASSAGE ON THIRD CONSIDERATION")', engine='python') \
        .rename(columns={
            'id': 'vote_event_id',
            'jurisdiction': 'state'
        }) \
        .loc[:, ['vote_event_id', 'bill_id', 'state']]

    votes = pd.read_csv('represent/tn_111/TN/111/TN_111_vote_people.csv') \
        .rename(columns={'voter_id': 'legislator_id'}) \
        .loc[:, ['vote_event_id', 'option', 'legislator_id']] \
        .merge(vote_events, on='vote_event_id', how='inner') \
        .drop(columns='vote_event_id')

    Vote = apps.get_model('legislators', 'Vote')
    Legislator = apps.get_model('legislators', 'Legislator')
    Bill = apps.get_model('bills', 'Bill')

    for v in votes.to_dict(orient='records'):
        vote = Vote.objects.create(state=v['state'], option=v['option'])

        try:
            b = Bill.objects.get(bill_id=v['bill_id'])
        except Bill.DoesNotExist:
            continue
        else:
            vote.bill_id.add(b)

        try:
            leg = Legislator.objects.get(legislator_id=v['legislator_id'])
        except Legislator.DoesNotExist:
            continue
        else:
            vote.legislator_id.add(leg)


class Migration(migrations.Migration):

    dependencies = [
        ('legislators', '0002_create_legislators'),
        ('bills', '0003_create_bills'),
    ]

    operations = [
        migrations.RunPython(create_legislator_votes)
    ]
