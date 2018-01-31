from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import *


def cv(request, cv_id):
    args = {'cv': get_object_or_404(CurriculumVitae, id=cv_id, user=request.user)}
    return render(request, 'cv/cv_full.html', args)
