from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(expenses)
admin.site.register(loan)
admin.site.register(Loantype)