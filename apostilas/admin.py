from django.contrib import admin
from .models import Apostila, Tags, ViewApostila, Avaliacao

admin.site.register(Apostila)
admin.site.register(ViewApostila)
admin.site.register(Tags)
admin.site.register(Avaliacao)