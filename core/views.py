from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, SignupForm, ProfileForm, QuestionForm, AnswerForm
from app.models import Question, Answer, Tag, Profile
from app.views import paginate, get_sidebar_context


def login_view(request):
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next_url = request.POST.get('next', '')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form, 'next': next_url, **get_sidebar_context()})


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form, **get_sidebar_context()})


def logout_view(request):
    logout(request)
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


@login_required(login_url='/login/')
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user, profile=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user, profile=profile)
    return render(request, 'core/profile.html', {'form': form, **get_sidebar_context()})


@login_required(login_url='/login/')
def ask_view(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect('one_question', pk=question.pk)
    else:
        form = QuestionForm()
    return render(request, 'core/ask.html', {'form': form, **get_sidebar_context()})


@login_required(login_url='/login/')
def add_answer_view(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            return redirect(reverse('one_question', kwargs={'pk': pk}) + f'#answer-{answer.pk}')
    return redirect('one_question', pk=pk)