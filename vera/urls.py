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
from vacancy import views as vacancy_views

basic = [
    path('', jobboard_views.index, name='index'),
    path('role/', jobboard_views.choose_role, name='choose_role'),
    path('admin/', admin.site.urls),
    path('account/', include("account.urls")),
    path('job/find/', jobboard_views.find_job, name='find_job'),
    path('profile/', jobboard_views.profile, name='profile'),
    path('help/', jobboard_views.user_help, name='user_help'),
    path('contract/status/change/', jobboard_views.change_contract_status, name='change_contract_status'),
    path('transactions/', jobboard_views.transactions, name='transactions'),
    path('withdraw/', jobboard_views.withdraw, name='withdraw'),
]

candidate_urlpatterns = [
    path('candidate/<int:candidate_id>/', jobboard_views.candidate, name='candidate'),
    path('candidate/approve/', jobboard_views.approve_candidate, name='approve_candidate'),
    path('candidate/revoke/', jobboard_views.revoke_candidate, name='revoke_candidate'),
    path('candidate/pay/<int:vacancy_id>/', jobboard_views.pay_to_candidate, name='pay_to_candidate'),
]

curriculum_vitae_urlpatterns = [
    path('cv/new/', cv_views.new_cv, name='new_cv'),
    path('cv/all/', cv_views.cv_all, name='cv_all'),
    path('cv/<int:cv_id>/', cv_views.cv, name='cv'),
    path('cv/<int:cv_id>/edit', cv_views.cv_edit, name='cv_edit'),
    path('cv/<int:cv_id>/new/position/', cv_views.new_position, name='new_position'),
    path('cv/<int:position_id>/edit/position/', cv_views.position_edit, name='position_edit'),
    path('cv/<int:cv_id>/new/education/', cv_views.new_education, name='new_education'),
    path('cv/<int:education_id>/edit/education/', cv_views.education_edit, name='education_edit'),
    path('cv/<int:cv_id>/new/experience/', cv_views.new_experience, name='new_experience'),
    path('cv/<int:experience_id>/edit/experience/', cv_views.experience_edit, name='experience_edit'),
    path('cv/<int:cv_id>/status/change/', cv_views.change_cv_status, name='change_cv_status'),
]

vacancy_urlpatterns = [
    path('vacancy/new/', vacancy_views.new_vacancy, name='new_vacancy'),
    path('vacancy/<int:vacancy_id>/subscribe/<int:cv_id>', vacancy_views.subscribe_to_vacancy,
         name='subscribe_to_vacancy'),
    path('vacancy/<int:vacancy_id>/', vacancy_views.vacancy, name='vacancy'),
    path('vacancy/<int:vacancy_id>/test/', jobboard_views.candidate_testing, name='candidate_testing'),
    path('vacancy/<int:vacancy_id>/edit/', vacancy_views.vacancy_edit, name='vacancy_edit'),
    path('vacancy/<int:vacancy_id>/tests/', vacancy_views.vacancy_tests, name='vacancy_tests'),
    path('vacancy/<int:vacancy_id>/tests/new/', vacancy_views.vacancy_test_new, name='vacancy_test_new'),
    path('vacancy/<int:vacancy_id>/status/change/', vacancy_views.change_vacancy_status, name='change_vacancy_status'),
    path('vacancy/tests/add/', vacancy_views.new_test, name='new_test'),
    # path('vacancy/increase/allowance', jobboard_views.increase_vacancy_allowance, name='increase_vacancy_allowance'),
    path('vacancy/all/', vacancy_views.vacancy_all, name='vacancy_all'),
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
