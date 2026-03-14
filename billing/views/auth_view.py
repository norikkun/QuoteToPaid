from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from billing.forms import LoginForm, UserCreateForm


class UserSetupView(CreateView):
    form_class = UserCreateForm
    model = User
    template_name = 'billing/users/user_form.html'
    success_url = reverse_lazy('billing:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('billing:user-detail')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        messages.success(self.request, 'ユーザーを登録し、ログインしました。')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'ユーザー登録',
                'page_heading': 'ユーザー登録',
                'page_description': '新しいアカウントを登録して、そのままログインできます。',
                'submit_label': '登録して開始する',
                'cancel_url': reverse_lazy('billing:login'),
            }
        )
        return context


class UserLoginView(LoginView):
    authentication_form = LoginForm
    redirect_authenticated_user = True
    template_name = 'billing/auth/login.html'

    def get_success_url(self):
        return self.get_redirect_url() or str(reverse_lazy('billing:dashboard'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'ログイン',
                'page_heading': 'ログイン',
                'page_description': '登録済みのユーザーでログインしてください。まだ未登録なら新規登録に進めます。',
            }
        )
        return context


class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'ログアウトしました。')
        return redirect('billing:login')
