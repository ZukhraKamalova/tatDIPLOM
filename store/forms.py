from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django import forms
from django.core.exceptions import ValidationError
from .models import Profile
import re

def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError('Пароль должен содержать минимум 8 символов')
    
    if not re.findall('[A-Z]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну ЗАГЛАВНУЮ букву')
    
    if not re.findall('[a-z]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну строчную букву')
    
    if not re.findall('[0-9]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну цифру')
    

    
    # Проверка на распространенные пароли
    common_passwords = ['password', '12345678', 'qwerty123', 'admin123', 'password123']
    if password.lower() in common_passwords:
        raise ValidationError('Этот пароль слишком распространен. Выберите другой.')

def validate_no_cyrillic_username(username):
    """Проверка, что имя пользователя не содержит кириллицу"""
    if re.search('[а-яА-Я]', username):
        raise ValidationError('Имя пользователя должно содержать только латинские буквы')

def validate_phone_number(phone):
    """Валидация номера телефона"""
    if phone and not re.match(r'^(\+7|8)[\d\s-]{10,}$', phone):
        raise ValidationError('Введите корректный номер телефона (например: +79991234567)')

class UserInfoForm(forms.ModelForm):
    phone = forms.CharField(
        label="", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}), 
        required=False,
        validators=[validate_phone_number] 
    )
    address1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Улица'}), required=False)
    address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Дом, квартира'}), required=False)
    city = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город'}), required=False)
    state = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Регион'}), required=False)
    zipcode = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Индекс'}), required=False)
    country = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Страна'}), required=False)
    
    class Meta:
        model = Profile
        fields = ('phone', 'address1', 'address2', 'city', 'state', 'zipcode', 'country')

class ChangePassword(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']
    
    def __init__(self, *args, **kwargs):
        super(ChangePassword, self).__init__(*args, **kwargs)
        
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Пароль'
        self.fields['new_password1'].label = ''
        self.fields['new_password1'].validators.append(validate_password_strength) 
        self.fields['new_password1'].help_text = '<ul class="form-text text-muted small">' \
            '<li>Минимум 8 символов</li>' \
            '<li>Минимум 1 заглавная буква (A-Z)</li>' \
            '<li>Минимум 1 строчная буква (a-z)</li>' \
            '<li>Минимум 1 цифра (0-9)</li>' \
            '</ul>'

        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Повторите пароль'
        self.fields['new_password2'].label = ''
        self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Повторите Ваш пароль для проверки.</small></span>'

    def clean_new_password1(self):
        """Дополнительная проверка пароля"""
        password = self.cleaned_data.get('new_password1')
        validate_password_strength(password)
        return password

class UpdateUserForm(UserChangeForm):
    password = None
    email = forms.EmailField(
        label="", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}), 
        required=False
    )
    first_name = forms.CharField(
        label="", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}), 
        required=False
    )
    last_name = forms.CharField(
        label="", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}), 
        required=False
    )
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        validators=[validate_no_cyrillic_username]  
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Только латинские буквы, цифры и @/./+/-/_.</small></span>'

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        label="", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        label="", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        validators=[validate_no_cyrillic_username]  
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Только латинские буквы, цифры и @/./+/-/_.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Пароль'
        self.fields['password1'].label = ''
        self.fields['password1'].validators.append(validate_password_strength) 
        self.fields['password1'].help_text = '<ul class="form-text text-muted small">' \
            '<li>Минимум 8 символов</li>' \
            '<li>Минимум 1 заглавная буква (A-Z)</li>' \
            '<li>Минимум 1 строчная буква (a-z)</li>' \
            '<li>Минимум 1 цифра (0-9)</li>' \
            '</ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Повторите пароль'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Повторите Ваш пароль для проверки.</small></span>'

    def clean_password1(self):
        """Дополнительная проверка пароля при регистрации"""
        password = self.cleaned_data.get('password1')
        validate_password_strength(password)
        return password

    def clean(self):
        """Проверка на совпадение паролей"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают!')
        
        return cleaned_data