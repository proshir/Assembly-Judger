from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('upload/', views.upload_problem, name='upload_problem'),
    path('problems/', views.problem_list, name='problem_list'),
    path('problems/<int:problem_id>/', views.view_problem, name='view_problem'),
    path('problems/<int:problem_id>/submit/', views.submit_solution, name='submit_solution'),
    path('submission/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('submissions/', views.view_submissions, name='view_submissions'),
]