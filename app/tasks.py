from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Sum, Q
from datetime import timedelta
import requests
import json

from .models import Tag, Profile, Question, Answer

POPULAR_TAGS_KEY = "popular_tags"
BEST_MEMBERS_KEY = "best_members"


# ─── Таска 1: популярные теги ─────────────────────────────────
@shared_task
def update_popular_tags():
    three_months_ago = timezone.now() - timedelta(days=90)

    tags = list(
        Tag.objects
        .filter(questions__created_at__gte=three_months_ago)
        .annotate(q_count=Count("questions"))
        .order_by("-q_count")
        .values("name", "q_count")[:10]
    )

    cache.set(POPULAR_TAGS_KEY, tags, timeout=60 * 60 * 3)
    return f"Updated {len(tags)} popular tags"


# ─── Таска 2: лучшие пользователи ─────────────────────────────
@shared_task
def update_best_members():
    week_ago = timezone.now() - timedelta(days=7)

    members = list(
        Profile.objects
        .annotate(
            score=(
                # сумма лайков на вопросы за неделю
                Count("user__questions__likes",
                      filter=Q(user__questions__created_at__gte=week_ago))
                +
                # сумма лайков на ответы за неделю
                Count("user__answers__likes",
                      filter=Q(user__answers__created_at__gte=week_ago))
            )
        )
        .order_by("-score")
        .values("user__username", "avatar", "score")[:10]
    )

    cache.set(BEST_MEMBERS_KEY, members, timeout=60 * 60)
    return f"Updated {len(members)} best members"


# ─── Таска 3: email автору вопроса ────────────────────────────
@shared_task
def send_answer_notification(question_id, answerer_username):
    try:
        question = Question.objects.select_related("author").get(pk=question_id)

        if not question.author.email:
            return "Author has no email"

        send_mail(
            subject=f'Новый ответ на ваш вопрос: "{question.title}"',
            message=(
                f"Здравствуйте, {question.author.username}!\n\n"
                f"Пользователь {answerer_username} ответил на ваш вопрос:\n"
                f'"{question.title}"\n\n'
                f"Посмотреть: http://localhost/question/{question_id}/"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[question.author.email],
            fail_silently=False,
        )
        return f"Email sent to {question.author.email}"

    except Question.DoesNotExist:
        return f"Question {question_id} not found"


# ─── Таска 4: уведомление в Centrifugo ────────────────────────
@shared_task
def notify_new_answer(question_id, answer_data):
    channel = f"question:{question_id}"

    try:
        response = requests.post(
            f"{settings.CENTRIFUGO_URL}/api/publish",
            headers={
                "Authorization": f"apikey {settings.CENTRIFUGO_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "channel": channel,
                "data": answer_data,
            }),
            timeout=5,
        )
        response.raise_for_status()
        return f"Notified channel {channel}"

    except requests.RequestException as e:
        return f"Centrifugo error: {e}"