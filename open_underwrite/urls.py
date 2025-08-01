from django.urls import path
from . import views

urlpatterns = [
    path('', views.loan_request, name='loan_request'),
    path('status/', views.loan_status, name='loan_status'),

    path('admin/status/', views.admin_status, name='admin_status'),
    path('admin/status/<str:passkey>/', views.admin_status_detail, name='admin_status_detail'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),

    path('train_model/', views.train_model, name='train_model'),
    path('submit_loan_request/', views.submit_loan_request, name='submit_loan_request'),
]
