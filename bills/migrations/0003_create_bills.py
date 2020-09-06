import pandas as pd
from django.db import migrations
from numpy import isnan

from bills.utils import tokenize, jaccard

bills = pd.read_csv('represent/tn_111/TN/111/TN_111_bills.csv') \
    .rename(columns={
        'jurisdiction': 'state',
        'subject': 'scraped_subjects',
        'id': 'bill_id',
        'identifier': 'name',
        'session_identifier': 'session',
        'organization_classification': 'chamber'
    }) \
    .drop(columns='classification') \
    .query('name.str.contains("HB|SB")', engine='python') \
    .assign(name=lambda x: x.name.str.replace(' ', '')) \
    .reset_index(drop=True)

# Scraped subjects is a list formatted as a string
bills['scraped_subjects'] = bills['scraped_subjects'].str.replace("\\[|\\]|\\'", '')

# Remove 'Amends TCA Title x, Chapter y' from bill titles
bills['title'] = bills['title'] \
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

os_tokens = bills['title'].apply(tokenize)
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

# Join companion bill
companion_bills = pd.read_csv('represent/tn_111/TN/111/TN_111_bill_related_bills.csv') \
    .loc[:, ['bill_id', 'identifier']] \
    .rename(columns={'identifier': 'companion_name'})

companion_bills['companion_name'] = \
    companion_bills['companion_name'].str.extract('(HB|SB)') + \
    companion_bills['companion_name'].str.extract('([0-9]{4})').astype(int).astype(str)

bills = bills.merge(companion_bills, on='bill_id', how='left')


def create_bills(apps, schema_editor):

    Bill = apps.get_model('bills', 'Bill')

    Bill.objects.bulk_create(
        [Bill(**b) for b in bills.to_dict(orient='records')]
    )


def create_add_subjects(apps, schema_editor):
    Bill = apps.get_model('bills', 'Bill')
    Subject = apps.get_model('bills', 'Subject')

    for bill, subject in zip(bills.to_dict(orient='rows'), subjects):
        b = Bill.objects.get(state=bill['state'], session=bill['session'], name=bill['name'])
        for sub in subject:
            # get_or_create returns a tuple with object and Boolean indicating whether created
            s = Subject.objects.get_or_create(subject=sub)
            b.subjects.add(s[0].id)


def create_actions(apps, schema_editor):
    actions = pd.read_csv('represent/tn_111/TN/111/TN_111_bill_actions.csv') \
        .rename(columns={
            'organization_id': 'actor',
            'description': 'action'
        }) \
        .merge(bills, on='bill_id', how='inner') \
        .loc[:, ['bill_id', 'session', 'name', 'action', 'actor', 'classification', 'date']] \
        .assign(state='Tennessee')

    # Scraped subjects is a list formatted as a string
    actions['classification'] = actions['classification'].str.replace("\\[|\\]|\\'", '')

    Action = apps.get_model('bills', 'Action')
    Bill = apps.get_model('bills', 'Bill')

    actions['bill_id'] = [Bill.objects.get(bill_id=i) for i in actions['bill_id']]

    Action.objects.bulk_create(
        [Action(**a) for a in actions.to_dict(orient='records')]
    )


def add_sponsors(apps, schema_editor):
    sponsors = pd.read_csv('represent/tn_111/TN/111/TN_111_bill_sponsorships.csv') \
        .assign(state='Tennessee')

    Bill = apps.get_model('bills', 'Bill')
    Legislator = apps.get_model('legislators', 'Legislator')

    for s in sponsors.to_dict(orient='records'):
        if not isinstance(s['person_id'], str):
            if isnan(s['person_id']):
                continue
        else:
            try:
                b = Bill.objects.get(bill_id=s['bill_id'])
            except Bill.DoesNotExist:
                continue
            else:
                leg = Legislator.objects.get(legislator_id=s['person_id'])
                b.sponsors.add(leg)


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0002_auto_20200905_2337'),
        ('legislators', '0002_create_legislators')
    ]

    operations = [
        migrations.RunPython(create_bills),
        migrations.RunPython(create_add_subjects),
        migrations.RunPython(create_actions),
        migrations.RunPython(add_sponsors)
    ]
