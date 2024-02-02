from django.contrib import admin
from .models import Batch, Product, TargetDate, Bay, Comment, DailyDiscussion
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Batch, SimpleHistoryAdmin)
admin.site.register(Product)
admin.site.register(TargetDate, SimpleHistoryAdmin)
admin.site.register(Bay)
admin.site.register(Comment)
admin.site.register(DailyDiscussion)
