from django.contrib import admin

# Register your models here.
import check.models

admin.site.register(check.models.Check)
