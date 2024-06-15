from django.urls import path
from .views import MovieListView, MovieDetailView, SeatMapView, register, custom_login_view, screenings_view
from django.contrib.auth.views import LoginView

from . import views

urlpatterns = [
    path('', MovieListView.as_view(), name='movie_list'),
    path('movies/<int:movie_id>/', MovieDetailView.as_view(), name='movie_detail'),
    path('seat_map/<int:movie_id>/', SeatMapView.as_view(), name='seat_map'),
    path('afisha/', views.afisha_view, name='afisha'),
    path('screenings/', views.screenings_view, name='screenings'),
    path('login/', LoginView.as_view(template_name='movies/login.html'), name='login'),
    path('register/', register, name='register'),
    path('custom_login/', custom_login_view, name='custom_login'),
    path('payment/', views.payment_page, name='payment_page'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('profile/', views.profile, name='profile'),
]