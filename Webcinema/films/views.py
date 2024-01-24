from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView, DetailView
from .models import Movie, Room


#class MovieView(View):

#    def get(self, request):
#        movies = Movie.objects.all()
#        return render(request, "movies/movie_list.html", {"movie_list": movies})


class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movie_list'


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    pk_url_kwarg = 'movie_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = Room.objects.first()
        context['room'] = room
        context['seat_map_url'] = reverse('seat_map', kwargs={'movie_id': self.object.pk})
        return context


class SeatMapView(View):
    template_name = 'movies/seat_map.html'

    def get(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, pk=movie_id)
        room = Room.objects.first()
        # Создаем диапазоны для рядов и мест в ряду
        rows = range(room.rows)
        seats = range(room.seats_per_row)

        context = {'movie': movie, 'room': room, 'rows': rows, 'seats': seats, 'seat_map_url': reverse('seat_map', kwargs={'movie_id': movie_id})}
        return render(request, self.template_name, context)

