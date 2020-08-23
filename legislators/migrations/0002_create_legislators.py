import pandas as pd
from django.db import migrations
from pyopenstates import search_legislators


def pull_legislators(apps, schema_editor):

    fields = [
        'leg_id', 'full_name', 'first_name', 'middle_name', 'last_name', 'suffix',
        'active', 'state', 'chamber', 'district', 'party', 'photo_url'
    ]

    # TODO: check on missing legislator IDs
    legislators = pd.DataFrame(search_legislators(state='tn')) \
        .loc[:, fields] \
        .dropna(subset=['district'])

    Legislator = apps.get_model('legislators', 'Legislator')

    for leg in legislators.to_dict(orient='records'):
        Legislator.objects.create(**leg)


class Migration(migrations.Migration):

    dependencies = [
        ('legislators', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(pull_legislators)
    ]
