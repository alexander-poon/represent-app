from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from legislators.models import Legislator


@login_required
def index(request):

	context = {
		'rep': Legislator.objects.get(leg_id=request.user.rep),
		'senator': Legislator.objects.get(leg_id=request.user.senator)
	}

	return render(request, 'legislators/index.html', context)


@login_required
def detail(request, pk):

	leg = Legislator.objects.get(pk=pk)

	context = {
		'legislator': leg,
		'bills': leg.bill_set.filter(session=111)
	}

	return render(request, 'legislators/detail.html', context)
