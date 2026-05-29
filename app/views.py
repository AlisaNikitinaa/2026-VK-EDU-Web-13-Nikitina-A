from django.shortcuts import render, redirect
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from .models import Question, Answer, Tag, Profile
from .tasks import send_answer_notification, notify_new_answer  # НОВОЕ


def paginate(queryset, request, per_page=5):
    paginator = Paginator(queryset, per_page)
    page_num = request.GET.get('page', 1)
    try:
        return paginator.page(page_num)
    except InvalidPage:
        raise Http404


# ИЗМЕНЕНО: убрали FIXED_TAGS, теперь берём из кеша с fallback в БД
def get_sidebar_context():
    # --- популярные теги ---
    popular_tags = cache.get("popular_tags")
    if popular_tags is None:
        three_months_ago = timezone.now() - timedelta(days=90)
        popular_tags = list(
            Tag.objects
            .filter(questions__created_at__gte=three_months_ago)
            .annotate(q_count=Count("questions"))
            .order_by("-q_count")
            .values("name", "q_count")[:10]
        )
        cache.set("popular_tags", popular_tags, timeout=60 * 60 * 3)

    # --- лучшие пользователи ---
    best_members = cache.get("best_members")
    if best_members is None:
        week_ago = timezone.now() - timedelta(days=7)
        best_members = list(
            Profile.objects
            .annotate(
                score=(
                    Count("user__questions__likes",
                          filter=Q(user__questions__created_at__gte=week_ago))
                    +
                    Count("user__answers__likes",
                          filter=Q(user__answers__created_at__gte=week_ago))
                )
            )
            .order_by("-score")
            .values("user__username", "avatar", "score")[:10]
        )
        cache.set("best_members", best_members, timeout=60 * 60)

    return {
        "popular_tags": popular_tags,
        "best_members": best_members,
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


# ИЗМЕНЕНО: добавили вызов тасок после сохранения ответа
def add_answer(request, pk):
    one_question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        answer = Answer.objects.create(
            question=one_question,
            author=request.user,
            text=request.POST.get('answer_text', ''),
        )
        # отправляем email автору вопроса
        send_answer_notification.delay(one_question.id, request.user.username)

        # уведомляем всех на странице вопроса через Centrifugo
        notify_new_answer.delay(one_question.id, {
            "id": answer.id,
            "author": request.user.username,
            "text": answer.text,
        })

    return redirect('one_question', pk=pk)


# НОВОЕ: полнотекстовый поиск
def search(request):
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({"results": []})

    questions = Question.objects.raw(
        """
        SELECT id, title,
               MATCH(title, text) AGAINST (%s IN BOOLEAN MODE) AS score
        FROM app_question
        WHERE MATCH(title, text) AGAINST (%s IN BOOLEAN MODE)
        ORDER BY score DESC
        LIMIT 10
        """,
        [query, query]
    )

    results = [{"id": q.id, "title": q.title} for q in questions]
    return JsonResponse({"results": results})