from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('results/', views.all_results, name='all_results'),
    path('results/<int:election_id>/', views.results, name='results'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Voter portal
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('election/<int:election_id>/', views.election_detail, name='election_detail'),
    path('election/<int:election_id>/success/', views.vote_success, name='vote_success'),

    # API
    path('api/votes/<int:election_id>/', views.live_vote_count, name='live_vote_count'),
]
