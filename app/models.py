import uuid
import os
from django.db import models
from django.contrib.auth.models import User


def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('avatars', filename)


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')

    def best(self):
        return self.order_by('-rating')

    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by('-created_at')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль: {self.user.username}'

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar
        return None


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name='Автор')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('question', kwargs={'pk': self.pk})

    def answer_count(self):
        return self.answers.count()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
    text = models.TextField(verbose_name='Текст')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'Ответ на «{self.question.title}» от {self.author.username}'


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes', verbose_name='Пользователь')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes', verbose_name='Вопрос')
    value = models.SmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        unique_together = ('user', 'question')

    def __str__(self):
        return f'{self.user.username} → {self.question.title}'


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes', verbose_name='Пользователь')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes', verbose_name='Ответ')
    value = models.SmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        unique_together = ('user', 'answer')

    def __str__(self):
        return f'{self.user.username} → ответ #{self.answer.pk}'