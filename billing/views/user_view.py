from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import DeleteView, TemplateView, UpdateView

from billing.forms import UserUpdateForm

from .base_view import AppLoginRequiredMixin


class CurrentUserMixin(AppLoginRequiredMixin):
    def get_object(self, queryset=None):
        return self.request.user


class UserDetailView(AppLoginRequiredMixin, TemplateView):
    template_name = 'billing/users/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'アカウント設定',
                'page_heading': 'アカウント設定',
                'user_obj': self.request.user,
            }
        )
        return context


class UserUpdateView(CurrentUserMixin, UpdateView):
    form_class = UserUpdateForm
    model = User
    template_name = 'billing/users/user_form.html'
    success_url = reverse_lazy('billing:user-detail')

    def form_valid(self, form):
        messages.success(self.request, 'ユーザー情報を更新しました。')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'アカウント編集',
                'page_heading': 'アカウント編集',
                'page_description': 'ご自身のログインユーザー情報を更新します。',
                'submit_label': '更新する',
                'cancel_url': reverse_lazy('billing:user-detail'),
            }
        )
        return context


class UserDeleteView(CurrentUserMixin, DeleteView):
    model = User
    template_name = 'billing/users/user_confirm_delete.html'
    success_url = reverse_lazy('billing:login')

    def form_valid(self, form):
        messages.success(self.request, 'ユーザーを削除しました。')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'アカウント削除',
                'page_heading': 'アカウント削除',
                'cancel_url': reverse_lazy('billing:user-detail'),
            }
        )
        return context
