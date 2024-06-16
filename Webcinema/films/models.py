from django.db import models


class Actor(models.Model):
    name = models.CharField("Имя актера", max_length=255)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    nationality = models.CharField("Национальность", max_length=100, null=True, blank=True)
    bio = models.TextField("Биография", null=True, blank=True)
    photo = models.ImageField("Фотография", upload_to='actor_photos/', null=True, blank=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    title = models.CharField("Название", max_length=255)
    genre = models.CharField("Жанр", max_length=100)
    release_date = models.DateField("Дата выхода")
    director = models.CharField("Режиссер", max_length=255)
    description = models.TextField("Описание")
    duration = models.DurationField("Длительность")
    actors = models.ManyToManyField(Actor, verbose_name="Актеры")
    poster = models.ImageField("Постер", upload_to='movie_posters/', null=True, blank=True)

    def __str__(self):
        return self.title


class Room(models.Model):
    room_number = models.IntegerField("Номер зала", primary_key=True)
    capacity = models.IntegerField("Вместимость")
    is_3d_capable = models.BooleanField("Возможность показа 3D")
    sound_system = models.CharField("Система звука", max_length=50)
    rows = models.PositiveIntegerField(default=8)  # Количество рядов
    seats_per_row = models.PositiveIntegerField(default=17)  # Мест в ряду

    def __str__(self):
        return f'Room {self.room_number}'


class Screening(models.Model):
    screening_id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    start_time = models.DateTimeField("Время начала")
    duration = models.DurationField("Длительность")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=1, verbose_name="Зал")

    def __str__(self):
        return f'Screening of {self.movie} at {self.start_time} in Room {self.room.room_number}'


class CustomUserManager(models.Manager):
    def create_user(self, email, username, password=None, **extra_fields):
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField("Email", unique=True)
    username = models.CharField("Имя пользователя", max_length=50, unique=True)
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Администратор", default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, verbose_name="Сеанс")
    seat_number = models.CharField("Номер места", max_length=10)
    reservation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата бронирования")
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f'Reservation for {self.screening} by {self.user}'


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat_number = models.CharField('Номер места', max_length=10)
    purchase_date = models.DateTimeField('Дата покупки', auto_now_add=True)

    def __str__(self):
        return f'Ticket #{self.ticket_id} - {self.screening} - Seat {self.seat_number}'
