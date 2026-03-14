from django.contrib.auth.forms import AuthenticationForm

TEXT_INPUT_CLASSES = (
    'mt-2 block w-full rounded-2xl border border-white/10 bg-stone-900/70 px-4 py-3 '
    'text-sm text-stone-100 placeholder:text-stone-500 focus:border-emerald-300 '
    'focus:outline-none focus:ring-2 focus:ring-emerald-300/30'
)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'ユーザー名'
        self.fields['password'].label = 'パスワード'
        self.fields['username'].widget.attrs['class'] = TEXT_INPUT_CLASSES
        self.fields['password'].widget.attrs['class'] = TEXT_INPUT_CLASSES
