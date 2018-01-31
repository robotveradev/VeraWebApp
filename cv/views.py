from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from jobboard.models import Candidate
from .models import *
from .forms import *


def cv(request, cv_id):
    args = {'cv': get_object_or_404(CurriculumVitae, id=cv_id, user=request.user)}
    return render(request, 'cv/cv_full.html', args)


def new_cv(request):
    can_o = get_object_or_404(Candidate, user=request.user)
    args = {'form': CurriculumVitaeForm(
        initial={'first_name': can_o.first_name,
                 'last_name': can_o.last_name,
                 'middle_name': can_o.middle_name})}
    if request.method == 'POST':
        args['form'] = CurriculumVitaeForm(request.POST, request.FILES)
        if args['form'].is_valid():
            s = args['form'].save(commit=False)
            s.user = request.user
            s.save()
    return render(request, 'cv/cv_new.html', args)
