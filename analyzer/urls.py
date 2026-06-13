from django.urls import path
from . import views

urlpatterns = [
    # Portal Landing
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    
    # Authentications
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student/register/', views.student_register_view, name='student_register'),
    path('company/register/', views.company_register_view, name='company_register'),
    
    # Student Candidate Endpoints
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('analyze/', views.analyze_resume_view, name='analyze_resume'),
    path('analysis/<int:pk>/', views.analysis_detail_view, name='analysis_detail'),
    path('analysis/<int:pk>/delete/', views.delete_analysis_view, name='delete_analysis'),
    path('jobs/', views.job_listings_view, name='job_listings'),
    path('jobs/<int:pk>/', views.job_detail_apply_view, name='job_detail'),
    
    # Company Employer Endpoints
    path('company/dashboard/', views.company_dashboard_view, name='company_dashboard'),
    path('company/jobs/create/', views.create_job_view, name='create_job'),
    path('company/jobs/<int:pk>/edit/', views.edit_job_view, name='edit_job'),
    path('company/jobs/<int:pk>/delete/', views.delete_job_view, name='delete_job'),
    path('company/jobs/<int:pk>/ranking/', views.candidate_ranking_view, name='candidate_ranking'),
    path('company/applications/<int:pk>/', views.candidate_detail_view, name='candidate_detail'),
]
