from django.views.generic import TemplateView


class DashboardTemplateView(TemplateView):
    template_name = 'billing/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'QuoteToPaid',
                'project_name': 'QuoteToPaid',
            }
        )
        return context
