from django.contrib import admin
from .models import (
    Batch,
    Product,
    TargetDate,
    Bay,
    Comment,
    DailyDiscussion,
    DailyDiscussionComment,
    Tray,
)
from simple_history.admin import SimpleHistoryAdmin

admin.site.site_header = "Packaging Priorities Admin"
admin.site.site_title = "Packaging Priorities Admin"

admin.site.register(Batch, SimpleHistoryAdmin)
admin.site.register(Product)
admin.site.register(TargetDate, SimpleHistoryAdmin)
admin.site.register(Bay)
admin.site.register(Comment)
admin.site.register(DailyDiscussion)
admin.site.register(DailyDiscussionComment, SimpleHistoryAdmin)
admin.site.register(Tray)
