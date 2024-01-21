from django.urls import path
from . import views

urlpatterns = [
    path("", views.batch_list, name="batch_list"),
    path("production_checks/", views.production_check_list, name="production_checks"),
    path("samples/", views.samples_list, name="samples_list"),
    path("warehouse/", views.warehouse_list, name="warehouse_list"),
    path("archive/", views.archive_list, name="archive_list"),
    path("bays/", views.bay_list, name="bay_list"),
    path("locations/", views.location, name="locations"),
    path("locations/<int:batch_id>/", views.locations, name="location"),
    path("products/", views.product_list, name="product_list"),
    path("batch_history/<int:batch_id>/", views.batch_history, name="batch_history"),
    path("batch/<int:batch_id>/", views.batch_detail, name="batch_detail"),
    path("completed_on/", views.CompletedOnView.as_view(), name="completed_on"),
    path(
        "batches_per_week_data/",
        views.batches_per_week_data,
        name="batches_per_week_data",
    ),
    path(
        "batches_per_week/",
        views.batches_per_week_chart,
        name="batches_per_week",
    ),
    path("add_batch/", views.add_batch, name="add_batch"),
    path("add_bay/", views.add_bay, name="add_bay"),
    path("add_product/", views.add_product, name="add_product"),
    path("edit_batch/<int:batch_id>/", views.edit_batch, name="edit_batch"),
    path("edit_bay/<int:bay_id>/", views.edit_bay, name="edit_bay"),
    path("edit_product/<int:product_id>/", views.edit_product, name="edit_product"),
    path("import_products/", views.import_products, name="import_products"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
]
