from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import VoteForm
from .models import Bill, Subject
from constituents.models import Vote


@login_required
def index(request):

	constituent_id = request.user.constituent_id
	votes = Vote.objects.filter(
		Q(name__contains='HB') | Q(companion_name='nan'),
		constituent_id=constituent_id
	)

	# subjects = Constituent.objects.get(constituent_id=constituent_id).subjects
	subjects = [i.id for i in Subject.objects.filter(subject__in=['Education'])]
	interest = Bill.objects.filter(
		Q(name__contains='HB') | Q(companion_name='nan'),
		subjects__in=subjects,
		session=111,
	)

	# Don't suggest bills constituent has already voted on
	for v in votes:
		interest = interest \
			.exclude(state=v.state, session=v.session, name=v.name) \
			.exclude(state=v.state, session=v.session, companion_name=v.name)

	context = {
		'support': votes.filter(position='support'),
		'oppose': votes.filter(position='oppose'),
		'interest': interest[:10]
	}

	return render(request, 'bills/index.html', context)


@login_required
def detail(request, state, session, name):
	b = get_object_or_404(Bill, state=state, session=session, name=name)

	try:
		p = Vote.objects.get(
			state=state,
			session=session,
			name=name,
			constituent=request.user.constituent_id
		).position
	except Vote.DoesNotExist:
		p = None

	if p in ['support', 'oppose']:
		position = f'You {p} this bill.'
	elif p == 'indifferent':
		position = 'You are indifferent toward this bill.'
	else:
		position = 'You have not expressed a position on this bill.'

	actions = b.get_actions()

	context = {
		'bill': b,
		'position': position,
		'support': b.count_votes(position='support'),
		'house_actions': actions.filter(actor='lower'),
		'senate_actions': actions.filter(actor='upper')
	}

	return render(request, 'bills/detail.html', context=context)


@login_required
def vote(request, state, session, name):
	constituent_id = request.user.constituent_id
	bill_id = Bill.objects.get(state=state, session=session, name=name)

	# Find companion bill (SB to HB) which may or may not exist
	try:
		companion_name = Bill.objects.get(
			state=state,
			session=session,
			name=name
		).companion_name
	except Bill.DoesNotExist:
		companion_name = None

	# Register vote for bill
	try:
		v = Vote.objects.get(
			state=state,
			session=session,
			name=name,
			constituent_id=constituent_id
		)
	except Vote.DoesNotExist:
		if request.method == 'POST':
			f = VoteForm(request.POST)
			if f.is_valid():
				v = f.save(commit=False)
				v.constituent_id = constituent_id
				v.bill_id = bill_id
				v.state = state
				v.session = session
				v.name = name
				v.companion_name = companion_name
				v.save()
	else:
		v.position = request.POST['position']
		v.save()

	# Register vote for companion bill if exists
	if companion_name is not None:
		try:
			c = Vote.objects.get(
				state=state,
				session=session,
				name=companion_name,
				constituent_id=constituent_id
			)
		except Vote.DoesNotExist:
			Vote.objects.create(
				bill_id=bill_id,
				state=state,
				session=session,
				name=companion_name,
				companion_name=name,
				constituent_id=constituent_id,
				position=request.POST['position']
			)
		else:
			c.position = request.POST['position']
			c.save()

	return HttpResponseRedirect(reverse('bills:detail', args=(state, session, name,)))
