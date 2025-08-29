from django.urls import path
from . import views

app_name = 'qa_api'

urlpatterns = [
    # Вопросы
    path('questions/', views.QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),

    # Ответы
    path('questions/<int:question_id>/answers/', views.AnswerCreateView.as_view(), name='answer-create'),
    path('answers/<int:pk>/', views.AnswerDetailView.as_view(), name='answer-detail'),
]