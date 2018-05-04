# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/cv/<int:cv_id>/', views.InterviewView.as_view(), name='interview'),
    path('action/new/interviewer/', views.NewInterviewerView.as_view(), name='new_interviewer'),
    # path('dialogs/<slug:username>', views.InterviewView.as_view(), name='interview'),
]
