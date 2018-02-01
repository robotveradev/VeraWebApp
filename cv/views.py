from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
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
            cv_saved_obj = args['form'].save(commit=False)
            cv_saved_obj.user = request.user
            cv_saved_obj.save()
            return redirect(cv, cv_id=cv_saved_obj.id)
    return render(request, 'cv/cv_new.html', args)


def new_position(request, cv_id):
    args = {'cv': cv_id}
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, user=request.user)
    args['form'] = PositionForm(request.POST or None)
    if args['form'].is_valid():
        s = args['form'].save()
        cv_o.position = s
        cv_o.save()
        return redirect(cv, cv_id=cv_id)
    return render(request, 'cv/new_position.html', args)


def new_education(request, cv_id):
    args = {'cv': cv_id}
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, user=request.user)
    args['form'] = EducationForm(request.POST or None)
    if args['form'].is_valid():
        s = args['form'].save()
        cv_o.education.add(s)
        cv_o.save()
        return redirect(cv, cv_id=cv_id)
    return render(request, 'cv/new_education.html', args)


def new_experience(request, cv_id):
    args = {'cv': cv_id}
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, user=request.user)
    args['form'] = ExperienceForm(request.POST or None)
    if args['form'].is_valid():
        s = args['form'].save()
        cv_o.experience.add(s)
        cv_o.save()
        return redirect(cv, cv_id=cv_id)
    return render(request, 'cv/new_experience.html', args)


def test(request):
    args = {}
    args['form'] = TestModelForm()
    return render(request, 'cv/test.html', args)