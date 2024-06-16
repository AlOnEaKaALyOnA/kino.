from django.urls import path
from .views import MovieListView, MovieDetailView, SeatMapView, register, custom_login_view, screenings_view, CustomLoginView, profile_view, save_reservation, save_booking_to_profile, load_booked_seats, load_selected_seats, clear_selected_seats
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    path('', MovieListView.as_view(), name='movie_list'),
    path('movies/<int:movie_id>/', MovieDetailView.as_view(), name='movie_detail'),
    path('seat_map/<int:movie_id>/', SeatMapView.as_view(), name='seat_map'),
    path('afisha/', views.afisha_view, name='afisha'),
    path('screenings/', views.screenings_view, name='screenings'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('custom_login/', custom_login_view, name='custom_login'),
    path('payment/', views.payment_page, name='payment_page'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('profile/', profile_view, name='profile'),
    path('save_reservation/', save_reservation, name='save_reservation'),
    path('save_booking_to_profile/', save_booking_to_profile, name='save_booking_to_profile'),
    path('load_booked_seats/', load_booked_seats, name='load_booked_seats'),
    path('load_selected_seats/', load_selected_seats, name='load_selected_seats'),
    path('clear_selected_seats/', views.clear_selected_seats, name='clear_selected_seats'),
]