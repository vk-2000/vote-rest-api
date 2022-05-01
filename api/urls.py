from django.urls import path
from .views import Result, Vote, ChoiceInfo, PollDetail, PollListAdd, Register, QuestionInfo, PollUpdateDelete

urlpatterns = [
    path('question/<int:pk>', QuestionInfo.as_view()),
    path('choice/<int:pk>', ChoiceInfo.as_view()),
    path('poll', PollListAdd.as_view()),
    path('poll/<int:pk>', PollUpdateDelete.as_view()),
    path('poll_detail/<int:pk>', PollDetail.as_view()),
    path('vote/<int:pk>', Vote.as_view()),
    path('result/<int:pk>', Result.as_view()),
    path('register', Register.as_view())
]
