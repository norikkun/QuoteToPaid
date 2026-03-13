from django.urls import path

from .views import DashboardTemplateView, HealthcheckView, InvoicePreviewPdfView

app_name = 'billing'

urlpatterns = [
    path('', DashboardTemplateView.as_view(), name='dashboard'),
    path('health/', HealthcheckView.as_view(), name='healthcheck'),
    path('pdf/preview/', InvoicePreviewPdfView.as_view(), name='pdf-preview'),
]
