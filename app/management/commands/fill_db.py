import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike

fake = Faker()

FIXED_TAGS = [
    'black-jack', 'bender', 'moon', 'python', 'debug', 'help',
    'django', 'database', 'MySQL', 'performance', 'perl', 'beginner',
    'learning', 'Firefox', 'javascript', 'extension', 'TechnoPark',
    'career', 'internship', 'Mail.Ru', 'API', 'integration',
    'Voloshin', 'literature', 'poetry', 'flask', 'tutorial'
]


class Command(BaseCommand):
    help = 'Заполнение БД тестовыми данными. Использование: python manage.py fill_db <ratio>'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения')

    def handle(self, *args, **options):
        ratio = options['ratio']

        self.stdout.write('Создаём теги...')
        tag_ids = self._create_tags(ratio)

        self.stdout.write('Создаём пользователей...')
        user_ids = self._create_users(ratio)

        self.stdout.write('Создаём вопросы...')
        question_ids = self._create_questions(ratio, user_ids, tag_ids)

        self.stdout.write('Создаём ответы...')
        answer_ids = self._create_answers(ratio, user_ids, question_ids)

        self.stdout.write('Создаём лайки...')
        self._create_likes(ratio, user_ids, question_ids, answer_ids)

        self.stdout.write(self.style.SUCCESS(f'Готово! ratio={ratio}'))

    def _create_tags(self, ratio):
        existing = set(Tag.objects.values_list('name', flat=True))
        to_create = [Tag(name=name) for name in FIXED_TAGS if name not in existing]
        existing.update(FIXED_TAGS)

        for _ in range(ratio - len(FIXED_TAGS)):
            name = f"{fake.word()}_{random.randint(1, 99999)}"
            if name not in existing:
                existing.add(name)
                to_create.append(Tag(name=name))

        Tag.objects.bulk_create(to_create, ignore_conflicts=True)
        return list(Tag.objects.values_list('id', flat=True))

    def _create_users(self, ratio):
        users = []
        for _ in range(ratio):
            username = f"{fake.user_name()}_{random.randint(1, 99999)}"
            users.append(User(
                username=username,
                email=fake.email(),
                password='pbkdf2_sha256$dummy',
            ))
        User.objects.bulk_create(users, ignore_conflicts=True)
        user_ids = list(User.objects.order_by('-id')[:ratio].values_list('id', flat=True))

        existing_profiles = set(Profile.objects.values_list('user_id', flat=True))
        profiles = [Profile(user_id=uid) for uid in user_ids if uid not in existing_profiles]
        Profile.objects.bulk_create(profiles, ignore_conflicts=True)
        return user_ids

    def _create_questions(self, ratio, user_ids, tag_ids):
        count = ratio * 10
        questions = [
            Question(
                author_id=random.choice(user_ids),
                title=fake.sentence()[:255],
                text=fake.text(max_nb_chars=1000),
                rating=random.randint(-10, 100),
            ) for _ in range(count)
        ]
        Question.objects.bulk_create(questions, batch_size=5000)
        question_ids = list(Question.objects.order_by('-id')[:count].values_list('id', flat=True))

        QuestionTag = Question.tags.through
        links = []
        for q_id in question_ids:
            chosen = random.sample(tag_ids, k=min(3, len(tag_ids)))
            for t_id in chosen:
                links.append(QuestionTag(question_id=q_id, tag_id=t_id))
        QuestionTag.objects.bulk_create(links, batch_size=10000, ignore_conflicts=True)
        return question_ids

    def _create_answers(self, ratio, user_ids, question_ids):
        count = ratio * 100
        batch_size = 10000
        buffer = []
        with transaction.atomic():
            for _ in range(count):
                buffer.append(Answer(
                    question_id=random.choice(question_ids),
                    author_id=random.choice(user_ids),
                    text=fake.text(max_nb_chars=500),
                    is_correct=random.random() < 0.1,
                    rating=random.randint(-5, 50),
                ))
                if len(buffer) >= batch_size:
                    Answer.objects.bulk_create(buffer)
                    buffer = []
            if buffer:
                Answer.objects.bulk_create(buffer)
        return list(Answer.objects.order_by('-id')[:count].values_list('id', flat=True))

    def _create_likes(self, ratio, user_ids, question_ids, answer_ids):
        count = ratio * 200
        batch_size = 20000

        # Лайки вопросов
        buffer = []
        seen = set()
        with transaction.atomic():
            attempts = 0
            while len(buffer) < count // 2 and attempts < count * 3:
                attempts += 1
                u = random.choice(user_ids)
                q = random.choice(question_ids)
                if (u, q) not in seen:
                    seen.add((u, q))
                    buffer.append(QuestionLike(user_id=u, question_id=q))
                if len(buffer) >= batch_size:
                    QuestionLike.objects.bulk_create(buffer, ignore_conflicts=True)
                    buffer = []
            if buffer:
                QuestionLike.objects.bulk_create(buffer, ignore_conflicts=True)

        # Лайки ответов
        buffer = []
        seen = set()
        with transaction.atomic():
            attempts = 0
            while len(buffer) < count // 2 and attempts < count * 3:
                attempts += 1
                u = random.choice(user_ids)
                a = random.choice(answer_ids)
                if (u, a) not in seen:
                    seen.add((u, a))
                    buffer.append(AnswerLike(user_id=u, answer_id=a))
                if len(buffer) >= batch_size:
                    AnswerLike.objects.bulk_create(buffer, ignore_conflicts=True)
                    buffer = []
            if buffer:
                AnswerLike.objects.bulk_create(buffer, ignore_conflicts=True)