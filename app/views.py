from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import random 


QUESTIONS = [
    {
        'id': 0,
        'title': 'How to build a moon park?',
        'text': 'Guys, i have trouble with a moon park. Can\'t find the black-jack...',
        'tags': ['black-jack', 'bender', 'moon'],
        'likes': 5,
        'answers': 3
    },
    {
        'id': 1,
        'title': 'Why is my Python code not working?',
        'text': 'I wrote a simple function but it keeps throwing an error...',
        'tags': ['python', 'debug', 'help'],
        'likes': 12,
        'answers': 7
    },
    {
        'id': 2,
        'title': 'Best practices for Django models?',
        'text': 'What are the best practices when creating Django models?',
        'tags': ['django', 'python', 'database'],
        'likes': 8,
        'answers': 4
    },
    {
        'id': 3,
        'title': 'How to optimize MySQL queries?',
        'text': 'My queries are running very slow, any suggestions?',
        'tags': ['MySQL', 'database', 'performance'],
        'likes': 15,
        'answers': 9
    },
    {
        'id': 4,
        'title': 'Learning Perl for beginners',
        'text': 'Where should I start learning Perl?',
        'tags': ['perl', 'beginner', 'learning'],
        'likes': 3,
        'answers': 1
    },
    {
        'id': 5,
        'title': 'Firefox extension development',
        'text': 'How to create a Firefox browser extension?',
        'tags': ['Firefox', 'javascript', 'extension'],
        'likes': 7,
        'answers': 2
    },
    {
        'id': 6,
        'title': 'TechnoPark internship tips',
        'text': 'Anyone has experience with TechnoPark internship?',
        'tags': ['TechnoPark', 'career', 'internship'],
        'likes': 4,
        'answers': 0
    },
    {
        'id': 7,
        'title': 'Mail.ru API integration',
        'text': 'How to integrate Mail.ru API into my project?',
        'tags': ['Mail.Ru', 'API', 'integration'],
        'likes': 6,
        'answers': 2
    },
    {
        'id': 8,
        'title': 'Voloshin poetry analysis',
        'text': 'Need help analyzing Voloshin\'s poems',
        'tags': ['Voloshin', 'literature', 'poetry'],
        'likes': 2,
        'answers': 0
    },
    {
        'id': 9,
        'title': 'Django vs Flask comparison',
        'text': 'Which framework is better for beginners?',
        'tags': ['django', 'flask', 'python'],
        'likes': 20,
        'answers': 15
    },
]

for i in range(10, 30):
    QUESTIONS.append({
        'id': i,
        'title': f'Question title {i}',
        'text': f'This is the text for question number {i}. It contains some interesting content.',
        'tags': ['python', 'help', 'question'] if i % 2 == 0 else ['django', 'tutorial'],
        'likes': i * 2,
        'answers': i % 5
    })



# Функция для генерации случайных ответов
def generate_answers(question_id, count):
    answers_texts = [
        "First of all I would like to thank you for the invitation to participate in such a... Russia is the huge territory which in many respects needs to be render habitable.",
        "This is a great question! Here is my answer: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "I had the same issue. Try checking your indentation and make sure all dependencies are installed.",
        "Thanks for asking! The best solution is to use a different approach. Let me explain...",
        "Actually, you might want to check the official documentation for this specific case.",
        "I disagree with the previous answer. Here's why I think differently...",
        "This is a common problem. Try restarting your server or clearing the cache.",
        "Have you tried looking at Stack Overflow? There's a great answer there with multiple solutions.",
        "I recommend reading this article, it explains everything in detail with examples.",
        "The answer is simpler than you think. Just change one line of code and it will work.",
        "This might help: check your indentation and variable names for typos.",
        "I solved this by updating to the latest version of the framework.",
        "Make sure you have all the required dependencies installed in your environment.",
        "It could be a caching issue. Try clearing your browser cache and restarting.",
        "I think you need to add an import statement at the top of your file.",
    ]
    
    authors = ["John Doe", "Jane Smith", "Mike Johnson", "Anna Brown", "Peter Parker", 
               "Bruce Wayne", "Clark Kent", "Diana Prince", "Tony Stark", "Steve Rogers",
               "Natasha Romanoff", "Thor Odinson", "Wanda Maximoff", "Stephen Strange"]
    
    answers = []
    for i in range(count):
        answer = {
            'id': i + 1,
            'author': random.choice(authors),
            'text': random.choice(answers_texts) + f" (Answer #{i+1} for question {question_id})",
            'is_correct': (i == 0 and random.choice([True, False])),  # только первый ответ может быть правильным
            'likes': random.randint(0, 20),
            'created_at': f"2024-0{random.randint(1, 12)}-{random.randint(10, 28)}"
        }
        answers.append(answer)
    
    return answers

# Кэш для хранения сгенерированных ответов (чтобы каждый раз не генерировать заново)
ANSWERS_CACHE = {}

def get_answers(question_id, count):
    cache_key = f"question_{question_id}"
    if cache_key not in ANSWERS_CACHE:
        ANSWERS_CACHE[cache_key] = generate_answers(question_id, count)
    return ANSWERS_CACHE[cache_key]

def index(request):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(QUESTIONS, per_page=5)
    page = paginator.page(page_num)
    return render(request, template_name="index.html", context={'questions': page.object_list, 'page_obj': page})

def question(request, question_id):
    # Находим вопрос
    one_question = None
    for q in QUESTIONS:
        if q['id'] == question_id:
            one_question = q
            break
    
    if one_question is None:
        return redirect('index')
    
    # Получаем количество ответов из вопроса
    answers_count = one_question.get('answers', 0)
    
    # Генерируем ответы динамически
    answers = get_answers(question_id, answers_count)
    
    return render(request, 'one_question.html', {
        'question': one_question,
        'answers': answers
    })

def ask_form(request):
    return render(request, 'ASK.html')

def profile(request):
    return render(request, 'profile.html')

def authorization(request):
    error = False
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            error = True
    return render(request, 'authorization.html', {'error': error})

def registration(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        avatar = request.FILES.get('avatar')
        
        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=username, email=email, password=password)
                    login(request, user)
                    return redirect('index')
                else:
                    error = "Sorry, this email address already registered!"
            else:
                error = "Sorry, this username already exists!"
        else:
            error = "Passwords don't match!"
    
    return render(request, 'registration.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('authorization')

def tag(request, tag_name):
    # Фильтруем вопросы по тегу
    filtered_questions = []
    for q in QUESTIONS:
        if tag_name in q.get('tags', []):
            filtered_questions.append(q)
    
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(filtered_questions, per_page=5)
    page = paginator.page(page_num)
    
    return render(request, 'tag.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tag_name': tag_name
    })

def add_answer(request, question_id):
    if request.method == 'POST':
        answer_text = request.POST.get('answer_text')
        
        # Обновляем количество ответов в вопросе
        for q in QUESTIONS:
            if q['id'] == question_id:
                q['answers'] = q.get('answers', 0) + 1
                break
        
        # Очищаем кэш для этого вопроса, чтобы при следующем просмотре сгенерировались новые ответы
        cache_key = f"question_{question_id}"
        if cache_key in ANSWERS_CACHE:
            del ANSWERS_CACHE[cache_key]
    
    return redirect('one_question', question_id=question_id)

def hot_questions(request):
    # Сортируем вопросы по количеству лайков (популярные)
    hot_questions_list = sorted(QUESTIONS, key=lambda x: x.get('likes', 0), reverse=True)
    
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(hot_questions_list, per_page=5)
    page = paginator.page(page_num)
    
    return render(request, 'hot_questions.html', {
        'questions': page.object_list,
        'page_obj': page
    })