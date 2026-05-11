from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from app.models import Question, Answer, Tag, Profile
from django.contrib.auth.password_validation import validate_password


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise ValidationError('Неверный логин или пароль')
        return cleaned_data

    def get_user(self):
        return self.user


class SignupForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password_confirm = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput())
    avatar = forms.ImageField(label='Аватар', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Пароли не совпадают')
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            avatar = self.cleaned_data.get('avatar')
            Profile.objects.create(user=user, avatar=avatar)
        return user
    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(label='Аватар', required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if self.profile:
            avatar = self.cleaned_data.get('avatar')
            if avatar:
                self.profile.avatar = avatar
                self.profile.save()
        return user


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        help_text='Введите теги через запятую',
        required=False,
    )

    class Meta:
        model = Question
        fields = ['title', 'text']

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            question.save()
            tags_str = self.cleaned_data.get('tags', '')
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            tag_objects = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                tag_objects.append(tag)
            question.tags.set(tag_objects)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']