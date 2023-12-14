from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(expenses)
admin.site.register(Loan)
admin.site.register(Payment)
admin.site.register(Loantype)
 


