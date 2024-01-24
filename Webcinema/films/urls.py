from django.urls import path
from .views import MovieListView, MovieDetailView, SeatMapView


from . import views

urlpatterns = [
    #path("", views.MovieView.as_view())
    path('', MovieListView.as_view(), name='movie_list'),
    path('movies/<int:movie_id>/', MovieDetailView.as_view(), name='movie_detail'),
    path('seat_map/<int:movie_id>/', SeatMapView.as_view(), name='seat_map'),
]