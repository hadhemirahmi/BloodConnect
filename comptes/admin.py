from django.contrib import admin

from .models import Donneur
admin.site.register(Donneur)
from .models import Hopital
admin.site.register(Hopital)
