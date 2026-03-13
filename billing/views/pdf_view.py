from django.http import HttpResponse
from django.views import View

from billing.services import InvoicePreviewPdfService


class InvoicePreviewPdfView(View):
    def get(self, request, *args, **kwargs):
        service = InvoicePreviewPdfService()
        response = HttpResponse(service.build_pdf(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{service.filename}"'
        return response
