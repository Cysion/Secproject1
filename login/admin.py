from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(User)
admin.site.register(RelationTo)
admin.site.register(RelationFrom)
admin.site.register(ResearchData)
admin.site.register(Action)
