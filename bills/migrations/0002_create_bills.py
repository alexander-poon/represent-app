import pandas as pd
from django.db import migrations
from pyopenstates import search_bills

from bills.utils import tokenize, jaccard

os_data = pd.DataFrame(search_bills(state='tn', search_window='all', type='bill')) \
    .query('bill_id.str.contains("HB|SB")', engine='python') \
    .assign(bill_id=lambda x: x.bill_id.str.replace(' ', ''))

# There are 200 pairs of duplicate bills; drop these
os_data = os_data[~os_data.duplicated(subset=['session', 'bill_id'])] \
    .reset_index(drop=True)

# Scraped subjects is a list; convert to a string
os_data['scraped_subjects'] = os_data['scraped_subjects'].apply(lambda x: '|'.join(x))

# Remove 'Amends TCA Title x, Chapter y' from bill titles
os_data['title'] = os_data['title'] \
    .str.replace(' - $', '') \
    .str.replace(' - Amends.+$', '') \
    .str.replace('^.+ - ', '')

# Subjects are all missing; fill them in with some educated guesses
# based on previously labeled data
labeled = pd.read_csv('represent/tn/tn_bills.csv') \
    .query('type=="bill"') \
    .reset_index(drop=True)

# Some subjects are nan; this causes problems with string methods
labeled['subjects'] = labeled['subjects'].fillna('')

os_tokens = os_data['title'].apply(tokenize)
labeled_tokens = labeled['title'].apply(tokenize)


def find_nearest_subject(bill):
    nearest_similarity = 0
    nearest_ix = 0

    for ix, title in enumerate(labeled_tokens):
        d = jaccard(bill, title)

        if d > nearest_similarity:
            nearest_similarity = d
            nearest_ix = ix

    return labeled['subjects'][nearest_ix].split('|')


subjects = [find_nearest_subject(i) for i in os_tokens]

fields = [
    'state', 'session', 'chamber', 'bill_id', 'title', 'scraped_subjects'
]

bills = os_data.loc[:, fields] \
    .assign(topics=None) \
    .to_dict(orient='records')


def create_bills(apps, schema_editor):

    Bill = apps.get_model('bills', 'Bill')

    for bill in bills:
        Bill.objects.create(**bill)


def create_add_subjects(apps, schema_editor):
    Bill = apps.get_model('bills', 'Bill')
    Subject = apps.get_model('bills', 'Subject')

    for bill, subject in zip(bills, subjects):
        b = Bill.objects.get(state=bill['state'], session=bill['session'], bill_id=bill['bill_id'])
        for sub in subject:
            # get_or_create returns a tuple with object and Boolean indicating whether created
            s = Subject.objects.get_or_create(subject=sub)
            b.subjects.add(s[0].id)


def create_actions(apps, schema_editor):
    actions = pd.DataFrame()

    for index, row in os_data.iterrows():
        actions = pd.concat([
            actions,
            pd.DataFrame(row['actions']).assign(
                state=row['state'],
                bill_id=row['bill_id'],
                session=row['session']
            )
        ])

    actions = actions \
        .loc[:, ['state', 'session', 'bill_id', 'action', 'actor', 'date']]

    Action = apps.get_model('bills', 'Action')

    for a in actions.to_dict(orient='records'):
        Action.objects.create(**a)


def add_sponsors(apps, schema_editor):
    sponsors = pd.DataFrame()

    for index, row in os_data.iterrows():
        sponsors = pd.concat([
            sponsors,
            pd.DataFrame(row['sponsors']).assign(
                state=row['state'],
                bill_id=row['bill_id'],
                session=row['session'],
                chamber=row['chamber']
            )
        ])

    Bill = apps.get_model('bills', 'Bill')
    Legislator = apps.get_model('legislators', 'Legislator')

    for s in sponsors.to_dict(orient='records'):
        b = Bill.objects.get(state=s['state'], session=s['session'], bill_id=s['bill_id'])
    # Since legislator IDs are missing have to match on name
        leg = Legislator.objects.filter(full_name=s['name'])
        if leg.count() == 1:
            b.sponsors.add(leg.first().pk)
        else:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0001_initial'),
        ('legislators', '0002_create_legislators')
    ]

    operations = [
        migrations.RunPython(create_bills),
        migrations.RunPython(create_add_subjects),
        migrations.RunPython(create_actions),
        migrations.RunPython(add_sponsors)
    ]
