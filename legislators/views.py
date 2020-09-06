from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from legislators.models import Legislator


@login_required
def index(request):

	context = {
		'rep': Legislator.objects.get(legislator_id=request.user.rep),
		'senator': Legislator.objects.get(legislator_id=request.user.senator)
	}

	return render(request, 'legislators/index.html', context)


@login_required
def detail(request, legislator_id):

	leg = Legislator.objects.get(legislator_id=legislator_id)

	context = {
		'legislator': leg,
		'bills': leg.bill_set.filter(session=111)
	}

	return render(request, 'legislators/detail.html', context)
