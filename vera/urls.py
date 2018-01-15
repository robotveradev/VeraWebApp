"""vera URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from jobboard import views as jobboard_views

urlpatterns = [
    path('', jobboard_views.index, name='index'),
    path('role/', jobboard_views.choose_role, name='choose_role'),
    path('admin/', admin.site.urls),
    path('account/', include("account.urls")),
    path('job/find/', jobboard_views.find_job, name='find_job'),
    path('settings/', jobboard_views.user_settings, name='settings'),
    path('vacancy/new/', jobboard_views.new_vacancy, name='new_vacancy'),
    path('vacancy/subscribe/', jobboard_views.subscrabe_to_vacancy, name='subscrabe_to_vacancy'),
    path('vacancy/<int:vacancy_id>/', jobboard_views.vacancy, name='vacancy'),
    path('candidate/<int:candidate_id>/', jobboard_views.candidate, name='candidate'),
    path('candidate/approve/', jobboard_views.approve_candidate, name='approve_candidate'),
]
