from django.contrib import admin
from .models import User, Donneur, Hopital

admin.site.register(Donneur)
admin.site.register(Hopital)