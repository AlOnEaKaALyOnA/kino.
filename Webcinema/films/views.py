from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView, DetailView
from .models import Movie, Room, Screening, Reservation
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.http import HttpResponseRedirect


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
        movie_screenings = Screening.objects.filter(movie=self.object)
        grouped_screenings = movie_screenings.values('start_time__date').annotate(count=Count('pk'))
        context['grouped_screenings'] = grouped_screenings
        context['room'] = room
        context['seat_map_url'] = reverse('seat_map', kwargs={'movie_id': self.object.pk})
        return context


class SeatMapView(View):
    template_name = 'movies/seat_map.html'

    def get(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, pk=movie_id)
        room = Room.objects.first()
        now = timezone.now()
        screening = Screening.objects.filter(movie=movie, start_time__gte=now).first()
        if not screening:
            context = {'movie': movie, 'room': room, 'no_screening': True}
            return render(request, self.template_name, context)

        # Создаем диапазоны для рядов и мест в ряду
        rows = range(room.rows)
        seats = range(room.seats_per_row)

        context = {
            'movie': movie,
            'room': room,
            'screening': screening,
            'rows': rows,
            'seats': seats,
            'seat_map_url': reverse('seat_map', kwargs={'movie_id': movie_id})
        }

        return render(request, self.template_name, context)


def afisha_view(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movie_list': movies})


def screenings_view(request):
    screenings = Screening.objects.all()
    return render(request, 'movies/screenings_list.html', {'screenings': screenings})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('movie_list')
    else:
        form = UserCreationForm()
    return render(request, 'movies/register.html', {'form': form})


def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('success_page')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Неверные учетные данные для входа в систему'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


class CustomLoginView(AuthLoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Вы успешно вошли в систему.')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Неверный адрес электронной почты или пароль. Пожалуйста, попробуйте снова.')
        return response


custom_login_view = CustomLoginView.as_view()


@require_POST
def save_reservation(request):
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    screening_id = request.POST.get('selected_screening')
    seat_number = request.POST.get('selected_seat')
    screening = Screening.objects.get(pk=screening_id)
    reservation = Reservation.objects.create(
        user=request.user,
        screening=screening,
        seat_number=seat_number,
        reservation_date=timezone.now(),
        email=email,
        phone=phone
    )

    return JsonResponse({'success': True})


def payment_page(request):
    return render(request, 'payment_page.html')


def process_payment(request):
    if request.method == 'POST':
        card_number = request.POST.get('cardNumber')
        expiry_date = request.POST.get('expiryDate')
        cvv = request.POST.get('cvv')
        return HttpResponseRedirect(reverse('payment_success'))
    else:

        return HttpResponseRedirect(reverse('payment_page'))


def payment_success(request):

    return render(request, 'payment_success.html')