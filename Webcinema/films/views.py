from django.contrib.auth.views import LoginView
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
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import logging


class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movie_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        if self.object_list.count() == 1:
            movie = self.object_list.first()
            return redirect('movie_detail', movie_id=movie.pk)
        context = self.get_context_data()
        return self.render_to_response(context)


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

@require_POST
def save_reservation(request):
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    screening_id = request.POST.get('selected_screening')
    seat_number = request.POST.get('selected_seat')
    screening = get_object_or_404(Screening, pk=screening_id)

    if request.user.is_authenticated:
        reservation = Reservation.objects.create(
            user=request.user,
            screening=screening,
            seat_number=seat_number,
            reservation_date=timezone.now(),
            email=request.user.email,
            phone=phone
        )
    else:
        reservation = Reservation.objects.create(
            screening=screening,
            seat_number=seat_number,
            reservation_date=timezone.now(),
            email=email,
            phone=phone
        )

    return JsonResponse({'success': True})


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
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('movie_list')
            else:
                messages.error(request, 'Неверные учетные данные для входа в систему')
    else:
        form = AuthenticationForm()
    return render(request, 'movies/login.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'movies/login.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


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


@login_required
def profile_view(request):
    return render(request, 'movies/profile.html', {'user': request.user})


logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
def save_booking_to_profile(request):
    if request.method == 'POST':
        try:

            logger.debug(f'Request body: {request.body}')

            data = json.loads(request.body)
            email = data.get('email')
            phone = data.get('phone')
            selected_seats = data.get('selected_seats', [])
            selected_screening_id = data.get('selected_screening')

            if not email or not phone or not selected_seats or not selected_screening_id:
                logger.error('Missing required fields in request data')
                return JsonResponse({'error': 'Все поля должны быть заполнены'}, status=400)
            screening = Screening.objects.get(id=selected_screening_id)
            user = request.user

            for seat in selected_seats:
                row = seat.get('row')
                seat_number = seat.get('seat')
                if row is None or seat_number is None:
                    logger.error('Invalid seat data in request')
                    return JsonResponse({'error': 'Некорректные данные для мест'}, status=400)

                Reservation.objects.create(
                    user=user,
                    screening=screening,
                    seat_number=f"{row}{seat_number}",
                    email=email,
                    phone=phone
                )

            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            logger.error('Invalid JSON in request body')
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
        except Screening.DoesNotExist:
            logger.error('Screening not found')
            return JsonResponse({'error': 'Screening не найден'}, status=404)
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            return JsonResponse({'error': str(e)}, status=500)

    logger.error('Invalid request method')
    return JsonResponse({'error': 'Неверный метод запроса'}, status=400)


@login_required
def load_booked_seats(request):
    try:
        user = request.user
        reservations = Reservation.objects.filter(user=user).values(
            'screening__movie__title',
            'screening__start_time',
            'seat_number',
            'reservation_date'
        )
        booked_seats = list(reservations)
        return JsonResponse({'bookedSeats': booked_seats})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def load_selected_seats(request):
    try:
        user = request.user
        reservations = Reservation.objects.filter(user=user).values('screening_id', 'seat_number')
        selected_seats = []
        for reservation in reservations:
            screening_id = reservation['screening_id']
            seat_number = reservation['seat_number']
            row, seat = seat_number.split(' ')
            row = row.replace('Row', '').strip()
            seat = seat.replace('Seat', '').strip()
            selected_seats.append({'row': row, 'seat': seat})
        return JsonResponse({'selectedSeats': selected_seats})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def clear_selected_seats(request):
    if request.method == 'POST':
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Метод не разрешен'}, status=405)