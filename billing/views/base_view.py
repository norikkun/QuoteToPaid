from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class AppLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('billing:login')
