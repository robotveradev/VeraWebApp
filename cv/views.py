from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from jobboard.models import CVOnVacancy
from .models import *
from .forms import *


def cv(request, cv_id):
    args = {'cv': get_object_or_404(CurriculumVitae, id=cv_id)}
    employers = [item['vacancy__employer__user'] for item in
                 CVOnVacancy.objects.values('vacancy__employer__user').filter(cv=args['cv'])]
    if args['cv'].candidate.user != request.user and request.user.id not in employers:
        raise Http404
    else:
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
            cv_saved_obj.candidate = can_o
            cv_saved_obj.save()
            return redirect(cv, cv_id=cv_saved_obj.id)
    return render(request, 'cv/cv_new.html', args)


def new_position(request, cv_id):
    args = {'cv': cv_id}
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, candidate__user=request.user)
    args['form'] = PositionForm(request.POST or None)
    if args['form'].is_valid():
        s = args['form'].save()
        cv_o.position = s
        cv_o.save()
        return redirect(cv, cv_id=cv_id)
    return render(request, 'cv/new_position.html', args)


def new_education(request, cv_id):
    args = {'cv': cv_id}
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, candidate__user=request.user)
    args['form'] = EducationForm(request.POST or None)
    if args['form'].is_valid():
        s = args['form'].save()
        cv_o.education.add(s)
        cv_o.save()
        return redirect(cv, cv_id=cv_id)
    return render(request, 'cv/new_education.html', args)


def new_experience(request, cv_id):
    args = {'cv': cv_id}
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, candidate__user=request.user)
    args['form'] = ExperienceForm(request.POST or None)
    if args['form'].is_valid():
        s = args['form'].save()
        cv_o.experience.add(s)
        cv_o.save()
        return redirect(cv, cv_id=cv_id)
    return render(request, 'cv/new_experience.html', args)


def change_cv_status(request, cv_id):
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, candidate__user=request.user)
    if cv_o.position is not None:
        cv_o.published = not cv_o.published
        cv_o.save()
    return redirect(cv, cv_id=cv_id)
