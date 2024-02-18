from django.urls import path
from . import views

urlpatterns = [
    path("", views.batch_list, name="batch_list"),
    path("search/", views.batch_search, name="batch_search"),
    path("schedule", views.schedule, name="schedule"),
    path("schedule/<int:week_offset>/", views.schedule, name="schedule_with_offset"),
    path("production_checks/", views.production_check_list, name="production_checks"),
    path("samples/", views.samples_list, name="samples_list"),
    path("warehouse/", views.warehouse_list, name="warehouse_list"),
    path("archive/", views.archive_list, name="archive_list"),
    path("bays/", views.bay_list, name="bay_list"),
    path("locations/", views.location, name="locations"),
    path("locations/<int:batch_id>/", views.locations, name="location"),
    path("products/", views.product_list, name="product_list"),
    path("wip-queue/", views.WIPQueueView.as_view(), name="wip_queue"),
    path("batch_history/<int:batch_id>/", views.batch_history, name="batch_history"),
    path("batch/<int:batch_id>/", views.batch_detail, name="batch_detail"),
    path(
        "edit_batch_htmx/<int:batch_id>/", views.edit_batch_htmx, name="edit_batch_htmx"
    ),
    path(
        "update_batch_htmx/<int:batch_id>/",
        views.update_batch_htmx,
        name="update_batch_htmx",
    ),
    path(
        "edit_target_dates/<int:bay_id>/<int:batch_id>/",
        views.edit_target_dates,
        name="edit_target_dates",
    ),
    path(
        "update_target_dates/<int:bay_id>/<int:batch_id>/",
        views.update_target_dates,
        name="update_target_dates",
    ),
    path("reports/completed_on/", views.CompletedOnView.as_view(), name="completed_on"),
    path(
        "batches_per_week_data/",
        views.batches_per_week_data,
        name="batches_per_week_data",
    ),
    path(
        "batches_per_user_per_week_data/",
        views.batches_per_user_per_week_data,
        name="batches_per_user_per_week_data",
    ),
    path(
        "batches_per_day_data/",
        views.batches_per_day_data,
        name="batches_per_day_data",
    ),
    path(
        "batches_completed_before_target_data/",
        views.batches_completed_before_target_data,
        name="batches_completed_before_target_data",
    ),
    path(
        "reports/batches_completed/",
        views.batches_completed,
        name="batches_completed",
    ),
    path("reports/team_leader_kpi/", views.team_leader_kpi, name="team_leader_kpi"),
    path("add_batch/", views.add_batch, name="add_batch"),
    path("add_bay/", views.add_bay, name="add_bay"),
    path("add_product/", views.add_product, name="add_product"),
    path("edit_batch/<int:batch_id>/", views.edit_batch, name="edit_batch"),
    path("edit_bay/<int:bay_id>/", views.edit_bay, name="edit_bay"),
    path("edit_product/<int:product_id>/", views.edit_product, name="edit_product"),
    path("import_products/", views.import_products, name="import_products"),
    path("signup/", views.signup, name="signup"),
    path("accounts/logout/", views.user_logout, name="logout"),
    path("daily_discussion/", views.daily_discussion, name="daily_discussion"),
    path(
        "daily_discussion/<str:date>/",
        views.daily_discussion,
        name="daily_discussion",
    ),
    path(
        "edit_discussion_comment/<int:comment_id>/",
        views.edit_discussion_comment,
        name="edit_discussion_comment",
    ),
    path("changelog/", views.changelog, name="changelog"),
]
