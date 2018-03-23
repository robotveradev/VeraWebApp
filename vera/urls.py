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
from django.views.generic import TemplateView
from jobboard import views as jobboard_views
from cv import views as cv_views
from vacancy import views as vacancy_views
from quiz import views as quiz_views

basic = [
    path('', jobboard_views.index, name='index'),
    path('role/', jobboard_views.ChooseRoleView.as_view(), name='choose_role'),
    path('admin/', admin.site.urls),
    path('account/', include("account.urls")),
    path('job/find/', jobboard_views.FindJobView.as_view(), name='find_job'),
    path('cv/find/', jobboard_views.FindCVView.as_view(), name='find_cv'),
    path('profile/', jobboard_views.ProfileView.as_view(), name='profile'),
    path('help/', TemplateView.as_view(template_name='jobboard/user_help.html'), name='user_help'),
    path('contract/status/change/', jobboard_views.change_contract_status, name='change_contract_status'),
    path('transactions/', jobboard_views.transactions, name='transactions'),
    path('withdraw/', jobboard_views.withdraw, name='withdraw'),
    path('check_agent/', jobboard_views.check_agent, name='check_agent'),
    path('agent/<slug:action>/', jobboard_views.GrantRevokeAgentView.as_view(), name='grant_agent'),
    path('fact/new/', jobboard_views.NewFactView.as_view(), name='new_fact'),
]

candidate_urlpatterns = [

]

curriculum_vitae_urlpatterns = [
    path('cv/new/', cv_views.new_cv, name='new_cv'),
    path('cv/all/', cv_views.cv_all, name='cv_all'),
    path('cv/<int:cv_id>/', cv_views.cv, name='cv'),
    path('cv/<int:cv_id>/edit/', cv_views.cv_edit, name='cv_edit'),
    path('cv/<int:cv_id>/new/position/', cv_views.new_position, name='new_position'),
    path('cv/<int:position_id>/edit/position/', cv_views.position_edit, name='position_edit'),
    path('cv/<int:cv_id>/new/education/', cv_views.new_education, name='new_education'),
    path('cv/<int:education_id>/edit/education/', cv_views.education_edit, name='education_edit'),
    path('cv/<int:cv_id>/new/experience/', cv_views.new_experience, name='new_experience'),
    path('cv/<int:experience_id>/edit/experience/', cv_views.experience_edit, name='experience_edit'),
    path('cv/<int:cv_id>/status/change/', cv_views.change_cv_status, name='change_cv_status'),
    path('cv/offer/', cv_views.VacancyOfferView.as_view(), name='offers'),
    path('hide/offer/<int:offer_id>', cv_views.HideOfferView.as_view(), name='hide_offer'),
]

vacancy_urlpatterns = [
    path('vacancy/new/', vacancy_views.new_vacancy, name='new_vacancy'),
    path('vacancy/<int:vacancy_id>/offer/<int:cv_id>/', vacancy_views.OfferVacancyView.as_view(),
         name='offer_vacancy'),
    path('vacancy/<int:vacancy_id>/subscribe/<int:cv_id>/', vacancy_views.subscribe_to_vacancy,
         name='subscribe_to_vacancy'),
    path('vacancy/<int:vacancy_id>/', vacancy_views.vacancy, name='vacancy'),
    path('vacancy/<int:vacancy_id>/edit/', vacancy_views.vacancy_edit, name='vacancy_edit'),
    path('vacancy/<int:vacancy_id>/status/change/', vacancy_views.change_vacancy_status, name='change_vacancy_status'),
    path('vacancy/all/', vacancy_views.vacancy_all, name='vacancy_all'),
]

quiz_urlpatterns = [
    path('quiz/', quiz_views.QuizIndexPage.as_view(), name='quiz_index'),
    path('quiz/category/<int:pk>', quiz_views.CategoryView.as_view(), name='category'),
    path('quiz/category/new/', quiz_views.NewCategoryView.as_view(), name='new_category'),
    path('quiz/category/<int:category_id>/question/new/', quiz_views.NewQuestionView.as_view(), name='new_question'),
    path('quiz/question/<int:question_id>/answer/new/', quiz_views.NewAnswerView.as_view(), name='new_answer'),
    path('quiz/<int:vacancy_id>/test/', quiz_views.CandidateTestingView.as_view(), name='candidate_testing'),
    path('quiz/vacancy/<int:vacancy_id>/tests/', quiz_views.VacancyTestsView.as_view(), name='vacancy_tests'),
    path('quiz/<int:vacancy_id>/tests/add/', quiz_views.VacancyAddTestsView.as_view(), name='vacancy_test_new'),
    path('quiz/<int:pk>/update/kind/', quiz_views.QuestionUpdateKindView.as_view(), name='update_question_kind'),
    path('quiz/exam/<int:pk>/update/grade/', quiz_views.ExamUpdateGradeView.as_view(), name='exam_update_grade'),
    path('quiz/test/answer/', quiz_views.ProcessAnswerView.as_view(), name='process_answer'),
    path('quiz/candidate/pay/<int:vacancy_id>/', quiz_views.PayToCandidateView.as_view(), name='pay_to_candidate'),
]

employer_urlpatterns = [
    path('employer/<int:employer_id>/about/', jobboard_views.employer_about, name='employer_about'),
    path('candidate/access/', jobboard_views.GrantRevokeCandidate.as_view(), name='access_candidate'),
]

urlpatterns = basic + \
              candidate_urlpatterns + \
              vacancy_urlpatterns + \
              quiz_urlpatterns + \
              curriculum_vitae_urlpatterns + \
              employer_urlpatterns + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
