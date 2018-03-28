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
from statistic import views as statistic_views

basic = [
    path('', TemplateView.as_view(template_name='jobboard/index.html'), name='index'),
    path('role/', jobboard_views.ChooseRoleView.as_view(), name='choose_role'),
    path('admin/', admin.site.urls),
    path('account/', include("account.urls")),
    path('job/find/', jobboard_views.FindJobView.as_view(), name='find_job'),
    path('cv/find/', jobboard_views.FindCVView.as_view(), name='find_cv'),
    path('profile/', jobboard_views.ProfileView.as_view(), name='profile'),
    path('help/', TemplateView.as_view(template_name='jobboard/user_help.html'), name='user_help'),
    path('contract/status/change/', jobboard_views.ChangeContractStatus.as_view(), name='change_contract_status'),
    path('transactions/', jobboard_views.TransactionsView.as_view(), name='transactions'),
    path('withdraw/', jobboard_views.withdraw, name='withdraw'),
    path('check_agent/', jobboard_views.check_agent, name='check_agent'),
    path('agent/<slug:action>/', jobboard_views.GrantRevokeAgentView.as_view(), name='grant_agent'),
    path('fact/new/', jobboard_views.NewFactView.as_view(), name='new_fact'),
]

candidate_urlpatterns = [

]

curriculum_vitae_urlpatterns = [
    path('cv/new/', cv_views.NewCvView.as_view(), name='new_cv'),
    path('cv/all/', cv_views.CvAllView.as_view(), name='cv_all'),
    path('cv/<int:pk>/', cv_views.CvView.as_view(), name='cv'),
    path('cv/<int:pk>/edit/', cv_views.CvEditView.as_view(), name='cv_edit'),
    path('cv/<int:pk>/position/new/', cv_views.NewPositionView.as_view(), name='new_position'),
    path('position/<int:pk>/edit/', cv_views.PositionEditView.as_view(), name='position_edit'),
    path('cv/<int:pk>/education/new/', cv_views.NewEducationView.as_view(), name='new_education'),
    path('education/<int:pk>/edit/', cv_views.EducationEditView.as_view(), name='education_edit'),
    path('cv/<int:pk>/experience/new/', cv_views.NewExperienceView.as_view(), name='new_experience'),
    path('experience/<int:pk>/edit/', cv_views.ExperienceEditView.as_view(), name='experience_edit'),
    path('cv/<int:pk>/status/change/', cv_views.ChangeCvStatusView.as_view(), name='change_cv_status'),
    path('cv/offer/', cv_views.VacancyOfferView.as_view(), name='offers'),
    path('hide/offer/<int:pk>', cv_views.HideOfferView.as_view(), name='hide_offer'),
]

vacancy_urlpatterns = [
    path('vacancy/new/', vacancy_views.CreateVacancyView.as_view(), name='new_vacancy'),
    path('vacancy/<int:vacancy_id>/offer/<int:cv_id>/', vacancy_views.OfferVacancyView.as_view(),
         name='offer_vacancy'),
    path('vacancy/<int:vacancy_id>/subscribe/<int:cv_id>/', vacancy_views.subscribe_to_vacancy,
         name='subscribe_to_vacancy'),
    path('vacancy/<int:pk>/', vacancy_views.VacancyView.as_view(), name='vacancy'),
    path('vacancy/<int:pk>/edit/', vacancy_views.VacancyEditView.as_view(), name='vacancy_edit'),
    path('vacancy/<int:pk>/status/change/', vacancy_views.ChangeVacancyStatus.as_view(), name='change_vacancy_status'),
    path('vacancy/all/', vacancy_views.VacanciesListView.as_view(), name='vacancy_all'),
]

quiz_urlpatterns = [
    path('quiz/', quiz_views.QuizIndexPage.as_view(), name='quiz_index'),
    path('quiz/category/<int:pk>', quiz_views.CategoryView.as_view(), name='category'),
    path('quiz/category/new/', quiz_views.NewCategoryView.as_view(), name='new_category'),
    path('quiz/category/<int:category_id>/question/new/', quiz_views.NewQuestionView.as_view(), name='new_question'),
    path('quiz/question/<int:question_id>/answer/new/', quiz_views.NewAnswerView.as_view(), name='new_answer'),
    path('quiz/<int:vacancy_id>/exam/', quiz_views.CandidateExaminingView.as_view(), name='candidate_examining'),
    path('quiz/vacancy/<int:vacancy_id>/exams/', quiz_views.VacancyExamView.as_view(), name='vacancy_exam'),
    path('quiz/<int:vacancy_id>/questions/add/', quiz_views.VacancyAddQuestionsView.as_view(), name='vacancy_exam_new'),
    path('quiz/<int:pk>/update/kind/', quiz_views.QuestionUpdateKindView.as_view(), name='update_question_kind'),
    path('quiz/exam/<int:pk>/update/grade/', quiz_views.ExamUpdateGradeView.as_view(), name='exam_update_grade'),
    path('quiz/process/answer/', quiz_views.ProcessAnswerView.as_view(), name='process_answer'),
    path('quiz/candidate/pay/<int:vacancy_id>/', quiz_views.PayToCandidateView.as_view(), name='pay_to_candidate'),
]

employer_urlpatterns = [
    path('employer/<int:pk>/about/', jobboard_views.EmployerAboutView.as_view(), name='employer_about'),
    path('candidate/access/', jobboard_views.GrantRevokeCandidate.as_view(), name='access_candidate'),
]

statistic_urlpatterns = [
    path('vacancy/<int:pk>/statistic/', statistic_views.StatisticView.as_view(), name='vacancystatistic'),
    path('cv/<int:pk>/statistic/', statistic_views.StatisticView.as_view(), name='cvstatistic'),
]

urlpatterns = basic + \
              candidate_urlpatterns + \
              vacancy_urlpatterns + \
              quiz_urlpatterns + \
              curriculum_vitae_urlpatterns + \
              employer_urlpatterns + \
              statistic_urlpatterns + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
