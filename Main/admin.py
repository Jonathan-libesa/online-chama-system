from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Members)
admin.site.register(Group)
admin.site.register(Grouptype)
admin.site.register(Category)
admin.site.register(Contribution)
admin.site.register(Cash)
