from django.contrib import admin

from .models import Movie, Screening, Room, User, Reservation, Actor, Ticket


admin.site.register(Movie)
admin.site.register(Screening)
admin.site.register(Room)
admin.site.register(User)
admin.site.register(Reservation)
admin.site.register(Actor)
admin.site.register(Ticket)