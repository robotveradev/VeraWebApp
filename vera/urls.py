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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from jobboard import views as jobboard_views
from cv import views as cv_views

basic = [
    path('', jobboard_views.index, name='index'),
    path('summernote/', include('django_summernote.urls')),
    path('test/', cv_views.test, name='test'),
    path('role/', jobboard_views.choose_role, name='choose_role'),
    path('admin/', admin.site.urls),
    path('account/', include("account.urls")),
    path('job/find/', jobboard_views.find_job, name='find_job'),
    path('profile/', jobboard_views.profile, name='profile'),
    path('help/', jobboard_views.user_help, name='user_help'),
    path('contract/status/change/', jobboard_views.change_contract_status, name='change_contract_status'),
]

candidate_urlpatterns = [
    path('candidate/<int:candidate_id>/', jobboard_views.candidate, name='candidate'),
    path('candidate/approve/', jobboard_views.approve_candidate, name='approve_candidate'),
    path('candidate/revoke/', jobboard_views.revoke_candidate, name='revoke_candidate'),
    path('candidate/pay/<int:vacancy_id>/', jobboard_views.pay_to_candidate, name='pay_to_candidate'),
]

curriculum_vitae_urlpatterns = [
    path('cv/new/', cv_views.new_cv, name='new_cv'),
    path('cv/<int:cv_id>/', cv_views.cv, name='cv'),
    path('cv/<int:cv_id>/new/position/', cv_views.new_position, name='new_position'),
    path('cv/<int:cv_id>/new/education/', cv_views.new_education, name='new_education'),
    path('cv/<int:cv_id>/new/experience/', cv_views.new_experience, name='new_experience'),
    path('cv/status/change/', jobboard_views.cnange_cv_status, name='change_cv_status'),
]

vacancy_urlpatterns = [
    path('vacancy/new/', jobboard_views.new_vacancy, name='new_vacancy'),
    path('vacancy/subscribe/', jobboard_views.subscrabe_to_vacancy, name='subscrabe_to_vacancy'),
    path('vacancy/<int:vacancy_id>/', jobboard_views.vacancy, name='vacancy'),
    path('vacancy/<int:vacancy_id>/test/', jobboard_views.candidate_testing, name='candidate_testing'),
    path('vacancy/<int:vacancy_id>/tests/', jobboard_views.vacancy_tests, name='vacancy_tests'),
    path('vacancy/<int:vacancy_id>/tests/new/', jobboard_views.vacancy_test_new, name='vacancy_test_new'),
    path('vacancy/<int:vacancy_id>/status/change/', jobboard_views.change_vacancy_status, name='change_vacancy_status'),
    path('vacancy/tests/add/', jobboard_views.new_test, name='new_test'),
]

employer_urlpatterns = [
    path('employer/<int:employer_id>/about/', jobboard_views.employer_about, name='employer_about'),
]

urlpatterns = basic + \
              candidate_urlpatterns + \
              vacancy_urlpatterns + \
              curriculum_vitae_urlpatterns + \
              employer_urlpatterns + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
