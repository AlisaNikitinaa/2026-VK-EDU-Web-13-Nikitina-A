from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator


QUESTIONS = [
    {
        'title': f'Title {i}',
        'id': i,
        'text': f'This is text for question # {i}'
    } for i in range(30)
]



def index(request):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(QUESTIONS, per_page=5)
    page = paginator.page(page_num)
    return render(request, template_name="index.html", context={'questions': page.object_list, 'page_obj': page})



def question(request, question_id):
    one_question = QUESTIONS[question_id]
    return render(
    request, template_name='one_question.html',
    context={'question': one_question} 
)
