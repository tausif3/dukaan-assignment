from django.contrib import admin
from django.urls import path, include
from main.views import (
    create_question,
    get_all_tags,
    top_questions,
    create_answer,
    create_comment,
    VoteView,
    search,
)

app_name = "user_management"


urlpatterns = [
    path("question/ask", create_question, name="create_question"),
    path("tags/", get_all_tags, name="get_all_tags"),
    path("top-questions/", top_questions, name="get_top_questions"),
    path("answer/", create_answer, name="create_answer"),
    path(
        "comment/<str:comment_category>/<int:pk>/",
        create_comment,
        name="create_comment",
    ),
    path("vote/<str:vote_type>/<int:pk>/", VoteView.as_view(), name="vote"),
    path("search", search, name="search"),
]
