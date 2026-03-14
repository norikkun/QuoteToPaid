from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

TEXT_INPUT_CLASSES = (
    'mt-2 block w-full rounded-2xl border border-white/10 bg-stone-900/70 px-4 py-3 '
    'text-sm text-stone-100 placeholder:text-stone-500 focus:border-emerald-300 '
    'focus:outline-none focus:ring-2 focus:ring-emerald-300/30'
)


class StyledUserFormMixin:
    """Apply a consistent Tailwind-friendly look to user forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = TEXT_INPUT_CLASSES


class UserCreateForm(StyledUserFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': 'ユーザー名',
            'first_name': '名',
            'last_name': '姓',
            'email': 'メールアドレス',
        }
        help_texts = {
            'username': 'ログインに利用するユーザーIDです。',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（確認）'
        self.fields['password1'].help_text = '8文字以上で設定してください。'
        self.fields['password2'].help_text = '確認のため同じパスワードを入力してください。'


class UserUpdateForm(StyledUserFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': 'ユーザー名',
            'first_name': '名',
            'last_name': '姓',
            'email': 'メールアドレス',
        }
