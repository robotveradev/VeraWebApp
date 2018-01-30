from django.http import HttpResponse
from django.shortcuts import render
from .models import *


def cv(request, cv_id):
    return HttpResponse(cv_id, status=200)
