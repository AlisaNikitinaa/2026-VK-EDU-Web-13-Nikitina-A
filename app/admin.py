from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike


# ─── Inlines ─────────────────────────────────────────────────────────────────

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = 'Профиль'
    verbose_name_plural = 'Профиль'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('author', 'rating', 'created_at')
    raw_id_fields = ('author',)


# ─── User (расширяем стандартный) ────────────────────────────────────────────

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


# ─── Profile ─────────────────────────────────────────────────────────────────

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)


# ─── Tag ─────────────────────────────────────────────────────────────────────

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# ─── Question ────────────────────────────────────────────────────────────────

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'rating', 'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('created_at', 'tags')
    raw_id_fields = ('author',)          # избегаем N+1 при выборе автора
    filter_horizontal = ('tags',)        # удобный виджет для ManyToMany
    inlines = (AnswerInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')


# ─── Answer ──────────────────────────────────────────────────────────────────

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'question', 'author', 'is_correct', 'rating', 'created_at')
    search_fields = ('text', 'author__username', 'question__title')
    list_filter = ('is_correct', 'created_at')
    raw_id_fields = ('author', 'question')   # без этого будет N+1

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'question')

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:60] + '…' if len(obj.text) > 60 else obj.text


# ─── QuestionLike ─────────────────────────────────────────────────────────────

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'question')
    search_fields = ('user__username', 'question__title')
    raw_id_fields = ('user', 'question')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'question')


# ─── AnswerLike ───────────────────────────────────────────────────────────────

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'answer')
    search_fields = ('user__username',)
    raw_id_fields = ('user', 'answer')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'answer')