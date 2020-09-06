import pandas as pd
from django.db import migrations


def create_legislators(apps, schema_editor):
    fields = [
        'legislator_id', 'name', 'given_name', 'family_name', 'state', 'chamber',
        'district', 'party', 'image'
    ]

    legislators = pd.read_csv('https://data.openstates.org/people/current/tn.csv') \
        .rename(columns={
            'id': 'legislator_id',
            'current_district': 'district',
            'current_chamber': 'chamber',
            'current_party': 'party',
        }) \
        .assign(state='Tennessee') \
        .loc[:, fields]

    Legislator = apps.get_model('legislators', 'Legislator')

    Legislator.objects.bulk_create(
        [Legislator(**leg) for leg in legislators.to_dict(orient='records')]
    )


class Migration(migrations.Migration):

    dependencies = [
        ('legislators', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_legislators)
    ]
