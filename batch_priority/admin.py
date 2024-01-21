from django.contrib import admin
from .models import Batch, Product, TargetDate, Bay
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Batch, SimpleHistoryAdmin)
admin.site.register(Product)
admin.site.register(TargetDate, SimpleHistoryAdmin)
admin.site.register(Bay)
