from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from main.serializers import (
    AnswerSerializer,
    QuestionSerializer,
    GetTagsSerializer,
    CommentSerializer,
)
from main import models
from main.constants import ANSWER, INCORRECT_URL, QUESTION
from main.utils import colon_regex, square_regex
from itertools import chain


@api_view(["POST"])
def create_question(request):
    "API to create a question."
    if request.method == "POST":
        serializer = QuestionSerializer(
            data=request.data,
            context={"media_urls": request.data.get("media_urls", None)},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_all_tags(request):
    "API to list all the existing tags."
    if request.method == "GET":
        queryset = models.Tags.objects.all()
        serialized = GetTagsSerializer(queryset, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def top_questions(request):
    if request.method == "GET":
        queryset = (
            models.Question.objects.prefetch_related("tags")
            .all()
            .order_by("-created_at")
        )
        serialized = QuestionSerializer(queryset, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_answer(request):
    if request.method == "POST":
        serializer = AnswerSerializer(
            data=request.data, context={"media_urls": request.data["media_urls"]}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def create_comment(request, comment_category, pk):
    """API to post a comment on a question or answer."""

    if request.method == "POST":
        if comment_category not in [ANSWER, QUESTION]:
            return JsonResponse(
                {"status": INCORRECT_URL}, status=status.HTTP_404_NOT_FOUND
            )

        context_data = {comment_category: pk}
        serializer = CommentSerializer(
            data=request.data,
            context=context_data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoteView(APIView):
    """API to (up/down)vote a question or answer."""

    def patch(self, request, vote_type, pk):
        if vote_type == ANSWER:
            answer = models.Answer.objects.get(pk=pk)
            serializer = AnswerSerializer(answer, data=request.data, partial=True)
        elif vote_type == QUESTION:
            question = models.Question.objects.get(id=pk)
            serializer = QuestionSerializer(question, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def search(request):
    """
    API to search across the platform.
    """
    query = request.GET.get("q")

    search_tag, search_term = square_regex(query)

    if search_tag and search_term:
        queryset = models.Question.objects.filter(
            Q(tags__name=search_tag),
            Q(body__contains=search_term) | Q(title__icontains=search_term),
        ).order_by("-vote")
        serialized = QuestionSerializer(queryset, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    elif colon_regex(query):
        title, body, search_text = colon_regex(query)
        if title:
            queryset = models.Question.objects.prefetch_related("comments").filter(
                title__icontains=search_text
            )
            serialized = QuestionSerializer(queryset, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)

        if body:
            queryset_one = models.Question.objects.prefetch_related("comments").filter(
                body__icontains=search_text
            )
            queryset_two = models.Answer.objects.prefetch_related("comments").filter(
                body__icontains=search_text
            )

            serialized_questions = QuestionSerializer(queryset_one, many=True)
            serialized_answers = AnswerSerializer(queryset_two, many=True)

            combined_data = serialized_answers.data + serialized_questions.data
            return Response(combined_data, status=status.HTTP_200_OK)
