from django.shortcuts import render, redirect
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Question, Answer, Tag, Profile


def paginate(queryset, request, per_page=5):
    paginator = Paginator(queryset, per_page)
    page_num = request.GET.get('page', 1)
    try:
        return paginator.page(page_num)
    except InvalidPage:
        raise Http404
FIXED_TAGS = [
    'perl',
    'python',
    'TechnoPark',
    'MySQL',
    'django',
    'Mail.Ru',
    'Voloshin',
    'Firefox'
]

def get_sidebar_context():
    return {
        'popular_tags': Tag.objects.filter(name__in=FIXED_TAGS),
    }


def index(request):
    questions = Question.objects.new().select_related('author__profile').prefetch_related('tags')
    page = paginate(questions, request)
    return render(request, 'index.html', {
        'page_obj': page,
        'questions': page.object_list,
        **get_sidebar_context(),
    })


def hot_questions(request):
    questions = Question.objects.best().select_related('author__profile').prefetch_related('tags')
    page = paginate(questions, request)
    return render(request, 'hot_questions.html', {
        'page_obj': page,
        'questions': page.object_list,
        **get_sidebar_context(),
    })


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name).select_related('author__profile').prefetch_related('tags')
    page = paginate(questions, request)
    return render(request, 'tag.html', {
        'page_obj': page,
        'questions': page.object_list,
        'tag': tag_obj,
        **get_sidebar_context(),
    })


def question(request, pk):
    one_question = get_object_or_404(
        Question.objects.select_related('author__profile').prefetch_related('tags'),
        pk=pk
    )
    answers = Answer.objects.filter(question=one_question).select_related('author__profile').order_by('-is_correct', '-rating')
    page = paginate(answers, request, per_page=10)
    return render(request, 'one_question.html', {
        'question': one_question,
        'page_obj': page,
        'answers': page.object_list,
        **get_sidebar_context(),
    })


def ask_form(request):
    return render(request, 'ASK.html', get_sidebar_context())


def profile(request):
    return render(request, 'profile.html', get_sidebar_context())


def authorization(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return redirect('index')
        return render(request, 'authorization.html', {'error': True, **get_sidebar_context()})
    return render(request, 'authorization.html', get_sidebar_context())


def registration(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            return render(request, 'registration.html', {'error': 'Пароли не совпадают', **get_sidebar_context()})
        if User.objects.filter(username=request.POST.get('username')).exists():
            return render(request, 'registration.html', {'error': 'Имя пользователя занято', **get_sidebar_context()})
        if User.objects.filter(email=request.POST.get('email')).exists():
            return render(request, 'registration.html', {'error': 'Email уже зарегистрирован', **get_sidebar_context()})

        user = User.objects.create_user(
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password=password,
        )
        Profile.objects.create(user=user, avatar=request.FILES.get('avatar'))
        login(request, user)
        return redirect('index')

    return render(request, 'registration.html', get_sidebar_context())


def logout_view(request):
    logout(request)
    return redirect('authorization')


def add_answer(request, pk):
    one_question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        Answer.objects.create(
            question=one_question,
            author=request.user,
            text=request.POST.get('answer_text', ''),
        )
    return redirect('one_question', pk=pk)