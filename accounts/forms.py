from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control login-input',
     'placeholder':'아이디', 'autofocus': True}))
    password = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control login-input',
         'placeholder':'비밀번호','autocomplete': 'current-password'}),
    )

class SignupForm(UserCreationForm):
    password1 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control signup-input',
         'placeholder':'비밀번호','autocomplete': 'current-password'}),
    )
    password2 = forms.CharField(
        label=("Password Confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control signup-input',
         'placeholder':'비밀번호 확인','autocomplete': 'current-password'}),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2',)
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control signup-input',
                'placeholder':'아이디', 'autofocus':True}),
            'email': forms.EmailInput(attrs={'class':'form-control signup-input',
                'placeholder':'이메일'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        has_email = get_user_model().objects.filter(email=email).exists()

        if has_email:
            try:
                raise forms.ValidationError('이미 등록된 이메일입니다.')
            except forms.ValidationError as error:
                self.add_error('email',  error)

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        print('email:', user.email)
        if commit:
            user.save()
        return user
