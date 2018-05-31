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
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from candidateprofile import views as cp_views
from company import views as company_views
from jobboard import views as jobboard_views
from pipeline import views as pipeline_views
from quiz import views as quiz_views
from statistic import views as statistic_views
from vacancy import views as vacancy_views

basic = [
    path('', TemplateView.as_view(template_name='jobboard/index.html'), name='index'),
    path('invite/<slug:code>/', jobboard_views.InviteLinkView.as_view(), name='invite_link'),
    path('role/', jobboard_views.ChooseRoleView.as_view(), name='choose_role'),
    path('admin/', admin.site.urls),
    path('account/signup/', jobboard_views.SignupInviteView.as_view(), name="account_signup"),
    path('account/', include("account.urls")),
    path('vacancies/', jobboard_views.FindJobView.as_view(), name='find_job'),
    path('profiles/', jobboard_views.FindCVView.as_view(), name='find_cv'),
    path('help/', TemplateView.as_view(template_name='jobboard/user_help.html'), name='user_help'),
    path('contract/status/change/', jobboard_views.ChangeContractStatus.as_view(), name='change_contract_status'),
    path('transactions/', jobboard_views.TransactionsView.as_view(), name='transactions'),
    path('withdraw/', jobboard_views.withdraw, name='withdraw'),
    path('approve/', jobboard_views.ApproveTokenView.as_view(), name='approve'),
    path('check_agent/', jobboard_views.check_agent, name='check_agent'),
    path('agent/<slug:action>/', jobboard_views.GrantRevokeAgentView.as_view(), name='grant_agent'),
    path('fact/new/', jobboard_views.NewFactView.as_view(), name='new_fact'),
    path('interview/', include('interview.urls')),
    path('free/coins/', jobboard_views.GetFreeCoinsView.as_view(), name='free_coins'),
]

candidate_urlpatterns = [
    path('profile/complete/', cp_views.CompleteProfileView.as_view(), name='complete_profile'),
    path('profile/', jobboard_views.ProfileView.as_view(), name='profile'),
    path('profile/id/<slug:username>/', jobboard_views.CandidateProfileView.as_view(), name='candidate_profile'),
    path('profile/new/language/', cp_views.NewLanguageView.as_view(), name='new_language'),
    path('profile/new/citizenship/', cp_views.NewCitizenshipView.as_view(), name='new_citizenship'),
    path('profile/new/workpermit/', cp_views.NewWorkPermitView.as_view(), name='new_work_permit'),
]

curriculum_vitae_urlpatterns = [
    path('profile/edit/', cp_views.CvEditView.as_view(), name='cv_edit'),
    path('position/new/', cp_views.NewPositionView.as_view(), name='new_position'),
    path('position/edit/', cp_views.PositionEditView.as_view(), name='position_edit'),
    path('education/new/', cp_views.NewEducationView.as_view(), name='new_education'),
    path('education/<int:pk>/edit/', cp_views.EducationEditView.as_view(), name='education_edit'),
    path('experience/new/', cp_views.NewExperienceView.as_view(), name='new_experience'),
    path('experience/<int:pk>/edit/', cp_views.ExperienceEditView.as_view(), name='experience_edit'),
    path('cv/offer/', cp_views.VacancyOfferView.as_view(), name='offers'),
    path('hide/offer/<int:pk>', cp_views.HideOfferView.as_view(), name='hide_offer'),
]

vacancy_urlpatterns = [
    path('vacancy/new/', vacancy_views.CreateVacancyView.as_view(), name='new_vacancy'),
    path('vacancy/<int:vacancy_id>/offer/<int:cv_id>/', vacancy_views.OfferVacancyView.as_view(),
         name='offer_vacancy'),
    path('vacancy/<int:vacancy_id>/subscribe/<int:cv_id>/', vacancy_views.SubscribeToVacancyView.as_view(),
         name='subscribe_to_vacancy'),
    path('vacancy/<int:pk>/', vacancy_views.VacancyView.as_view(), name='vacancy'),
    path('vacancy/<int:pk>/edit/', vacancy_views.VacancyEditView.as_view(), name='vacancy_edit'),
    path('vacancy/<int:pk>/status/change/', vacancy_views.ChangeVacancyStatus.as_view(), name='change_vacancy_status'),
    path('vacancy/all/', vacancy_views.VacanciesListView.as_view(), name='vacancy_all'),
    path('vacancy/<int:pk>/update_allowed/', vacancy_views.UpdateAllowedView.as_view(), name='update_allowed'),
]

quiz_urlpatterns = [
    path('quiz/', quiz_views.QuizIndexPage.as_view(), name='quiz_index'),
    path('quiz/category/<int:pk>', quiz_views.CategoryView.as_view(), name='category'),
    path('quiz/category/new/', quiz_views.NewCategoryView.as_view(), name='new_category'),
    path('quiz/category/<int:category_id>/question/new/', quiz_views.NewQuestionView.as_view(), name='new_question'),
    path('quiz/question/<int:question_id>/answer/new/', quiz_views.NewAnswerView.as_view(), name='new_answer'),
    path('quiz/<int:pk>/exam/<int:cv_id>', quiz_views.CandidateExaminingView.as_view(), name='candidate_examining'),
    path('quiz/<int:pk>/questions/add/', quiz_views.ActionAddQuestionsView.as_view(), name='action_exam_new'),
    path('quiz/<int:pk>/update/kind/', quiz_views.QuestionUpdateKindView.as_view(), name='update_question_kind'),
    path('quiz/exam/<int:pk>/update/grade/', quiz_views.ExamUpdateGradeView.as_view(), name='exam_update_grade'),
    path('quiz/process/answer/', quiz_views.ProcessAnswerView.as_view(), name='process_answer'),
    # path('quiz/candidate/pay/<int:vacancy_id>/', quiz_views.PayToCandidateView.as_view(), name='pay_to_candidate'),
    path('quiz/action/<int:pk>/exam/', quiz_views.ActionExamView.as_view(), name='action_exam'),
    path('quiz/exam/<int:pk>/result/', quiz_views.ExamResultsView.as_view(), name='exam_results'),
]

employer_urlpatterns = [
    path('employer/<int:pk>/about/', jobboard_views.EmployerAboutView.as_view(), name='employer_about'),
    path('companies/', company_views.CompaniesView.as_view(), name='companies'),
    path('company/new/', company_views.NewCompanyView.as_view(), name='new_company'),
    path('company/<int:pk>', company_views.CompanyDetailsView.as_view(), name='company'),
    path('company/<int:pk>/delete/', company_views.CompanyDeleteView.as_view(), name='delete_company'),
    path('company/<int:pk>/office/new/', company_views.CompanyNewOfficeView.as_view(), name='new_office'),
    path('soclink/new/', company_views.NewSocialLink.as_view(), name='new_social_link'),
]

statistic_urlpatterns = [
    path('vacancy/<int:pk>/statistic/', statistic_views.StatisticView.as_view(), name='vacancystatistic'),
    path('cv/<int:pk>/statistic/', statistic_views.StatisticView.as_view(), name='cvstatistic'),
]

pipeline_urlpatterns = [
    path('vacancy/<int:pk>/pipeline/', pipeline_views.PipelineConstructorView.as_view(), name='pipeline_constructor'),
    path('vacancy/<int:vacancy_id>/approve/<int:cv_id>/', pipeline_views.ApproveActionEmployerView.as_view(),
         name='employer_approve_action'),
    path('vacancy/<int:vacancy_id>/revoke/<int:cv_id>/', pipeline_views.RevokeCvEmployerView.as_view(),
         name='employer_revoke'),
    path('vacancy/<int:pk>/action/<int:action_id>/details/', pipeline_views.ActionDetailView.as_view(),
         name='action_details'),
]

interview_urlpatterns = [
    # path('interview/', TemplateView.as_view(template_name='interview/interview_page.html')),
]

urlpatterns = basic + \
              candidate_urlpatterns + \
              vacancy_urlpatterns + \
              quiz_urlpatterns + \
              curriculum_vitae_urlpatterns + \
              employer_urlpatterns + \
              statistic_urlpatterns + \
              pipeline_urlpatterns + \
              interview_urlpatterns + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
