from account.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from jobboard.decorators import choose_role_required
from vacancy.models import CVOnVacancy
from jobboard.models import Candidate
from .forms import *


def cv(request, cv_id):
    args = {'cv': get_object_or_404(CurriculumVitae, id=cv_id)}
    employers = [item['vacancy__employer__user'] for item in
                 CVOnVacancy.objects.values('vacancy__employer__user').filter(cv=args['cv'])]
    if args['cv'].candidate.user != request.user and request.user.id not in employers:
        raise Http404
    else:
        return render(request, 'cv/cv_full.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
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


@login_required
@choose_role_required(redirect_url='/role/')
def new_position(request, cv_id):
    args = {'cv': cv_id}
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, candidate__user=request.user)
    args['form'] = PositionForm(request.POST or None)
    if args['form'].is_valid():
        s = args['form'].save()
        cv_o.position = s
        cv_o.published = True
        cv_o.save()
        return redirect(cv, cv_id=cv_id)
    return render(request, 'cv/new_position.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
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


@login_required
@choose_role_required(redirect_url='/role/')
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


@login_required
@choose_role_required(redirect_url='/role/')
def change_cv_status(request, cv_id):
    cv_o = get_object_or_404(CurriculumVitae, id=cv_id, candidate__user=request.user)
    if cv_o.position is not None:
        cv_o.published = not cv_o.published
        cv_o.save()
    return redirect(cv, cv_id=cv_id)


@login_required
@choose_role_required(redirect_url='/role/')
def cv_all(request):
    args = {}
    args['cv'] = CurriculumVitae.objects.filter(candidate__user=request.user)
    return render(request, 'cv/cv_all.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def cv_edit(request, cv_id):
    args = {}
    args['cv_o'] = get_object_or_404(CurriculumVitae, candidate__user=request.user, pk=cv_id)
    if request.method == 'POST':
        form = CurriculumVitaeForm(request.POST, request.FILES, instance=args['cv_o'])
        if form.is_valid():
            form.save()
            return redirect(cv, cv_id=cv_id)
    else:
        form = CurriculumVitaeForm(instance=args['cv_o'])
    args['form'] = form
    return render(request, 'cv/cv_edit.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def position_edit(request, position_id):
    args = {}
    args['position_o'] = get_object_or_404(Position, pk=position_id)
    cv_o = get_object_or_404(CurriculumVitae, position=args['position_o'], candidate__user=request.user)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=args['position_o'])
        if form.is_valid():
            form.save()
            return redirect(cv, cv_id=cv_o.id)
    else:
        form = PositionForm(instance=args['position_o'])
    args['form'] = form
    return render(request, 'cv/position_edit.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def experience_edit(request, experience_id):
    args = {}
    args['exp_o'] = get_object_or_404(Experience, pk=experience_id)
    cv_o = get_object_or_404(CurriculumVitae, experience__in=[experience_id, ], candidate__user=request.user)
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=args['exp_o'])
        if form.is_valid():
            form.save()
            return redirect(cv, cv_id=cv_o.id)
    else:
        form = ExperienceForm(instance=args['exp_o'])
    args['form'] = form
    return render(request, 'cv/experience_edit.html', args)


@login_required
@choose_role_required(redirect_url='/role/')
def education_edit(request, education_id):
    args = {}
    args['edu_o'] = get_object_or_404(Education, pk=education_id)
    cv_o = get_object_or_404(CurriculumVitae, education__in=[education_id, ], candidate__user=request.user)
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=args['edu_o'])
        if form.is_valid():
            form.save()
            return redirect(cv, cv_id=cv_o.id)
    else:
        form = EducationForm(instance=args['edu_o'])
    args['form'] = form
    return render(request, 'cv/education_edit.html', args)