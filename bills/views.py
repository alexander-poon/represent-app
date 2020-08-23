from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import VoteForm
from .models import Bill, Subject
from constituents.models import Vote


@login_required
def index(request):

	constituent_id = request.user.constituent_id

	# subjects = Constituent.objects.get(constituent_id=constituent_id).subjects
	subjects = [i.id for i in Subject.objects.filter(subject__in=['Education'])]

	support = Vote.objects.filter(constituent_id=constituent_id, position='support')
	oppose = Vote.objects.filter(constituent_id=constituent_id, position='oppose')
	indifferent = Vote.objects.filter(constituent_id=constituent_id, position='indifferent')
	interest = Bill.objects.filter(subjects__in=subjects, session=111)

	# Don't suggest bills constituent has already voted on
	for b in (support | oppose | indifferent):
		interest = interest.exclude(state=b.state, session=b.session, bill_id=b.bill_id)

	context = {
		'support': support,
		'oppose': oppose,
		'interest': interest[:10]
	}

	return render(request, 'bills/index.html', context)


@login_required
def detail(request, state, session, bill_id):
	bill = get_object_or_404(Bill, state=state, session=session, bill_id=bill_id)

	try:
		p = Vote.objects.get(
			state=state,
			session=session,
			bill_id=bill_id,
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

	actions = bill.get_actions()

	context = {
		'bill': bill,
		'position': position,
		'support': bill.count_votes(position='support'),
		'house_actions': actions.filter(actor='lower'),
		'senate_actions': actions.filter(actor='upper')
	}

	return render(request, 'bills/detail.html', context=context)


@login_required
def vote(request, state, session, bill_id):

	try:
		v = Vote.objects.get(
			state=state,
			session=session,
			bill_id=bill_id,
			constituent_id=request.user.constituent_id
		)
	except Vote.DoesNotExist:
		if request.method == 'POST':
			f = VoteForm(request.POST)
			if f.is_valid():
				v = f.save(commit=False)
				v.constituent_id = request.user.constituent_id
				v.state = state
				v.session = session
				v.bill_id = bill_id
				v.save()
	else:
		v.position = request.POST['position']
		v.save()

	return HttpResponseRedirect(reverse('bills:detail', args=(state, session, bill_id,)))
