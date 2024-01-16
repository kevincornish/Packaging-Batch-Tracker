from django.urls import path
from . import views

urlpatterns = [
    path('', views.batch_list, name='batch_list'),
    path('production_checks/', views.production_check_list, name='production_checks'),
    path('samples/', views.samples_list, name='samples_list'),
    path('warehouse/', views.warehouse_list, name='warehouse_list'),
    path('archive/', views.archive_list, name='archive_list'),
    path('bays/', views.bay_list, name='bay_list'),
    path('products/', views.product_list, name='product_list'),
    path('add_batch/', views.add_batch, name='add_batch'),
    path('add_bay/', views.add_bay, name='add_bay'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_batch/<int:batch_id>/', views.edit_batch, name='edit_batch'),
    path('edit_bay/<int:bay_id>/', views.edit_bay, name='edit_bay'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('import_products/', views.import_products, name='import_products'),
]