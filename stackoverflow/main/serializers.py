from rest_framework import serializers
from django.contrib.auth import get_user_model
from main import models
from user_management.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from main.constants import ANSWER, QUESTION, UPVOTE, DOWNVOTE, VALUE

User = get_user_model()


class QuestionSerializer(serializers.ModelSerializer):
    "Serializer class for a question."

    tags = serializers.SlugRelatedField(
        many=True, queryset=models.Tags.objects.all(), slug_field="name"
    )
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = models.Question
        fields = ("title", "body", "created_by", "tags", "created_at", "vote")

    def create(self, validated_data):
        tags = None

        if validated_data.get("tags", None):
            tags = validated_data.pop("tags")

        question = super(QuestionSerializer, self).create(validated_data)
        if tags:
            question.tags.add(*tags)

        if self.context.get("media_urls", None):
            media_urls = [
                models.MultiMedia(media_url=url, content_object=question)
                for url in self.context.pop("media_urls")
            ]

            question.media_urls.bulk_create(media_urls)

        return question

    def update(self, question, validated_data):
        vote = validated_data.get("vote")
        if vote == UPVOTE:
            question.vote = F("vote") + VALUE
        elif vote == DOWNVOTE:
            question.vote = F("vote") - VALUE

        question.save(update_fields=["vote"])
        question.refresh_from_db()
        return question


class GetTagsSerializer(serializers.ModelSerializer):
    "Serializer class to get all tags."

    class Meta:
        model = models.Tags
        fields = ("id", "name", "description")


class AnswerSerializer(serializers.ModelSerializer):
    "Serializer class for an answer."

    question = serializers.PrimaryKeyRelatedField(
        queryset=models.Question.objects.all()
    )
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = models.Answer
        fields = (
            "id",
            "body",
            "question",
            "vote",
            "created_at",
            "created_by",
        )

    def create(self, validated_data):
        answer = super(AnswerSerializer, self).create(validated_data)
        media_urls = [
            models.MultiMedia(media_url=url, content_object=answer)
            for url in self.context.pop("media_urls")
        ]
        answer.media_urls.bulk_create(media_urls)
        return answer

    def update(self, answer, validated_data):
        vote = validated_data.get("vote")
        if vote == UPVOTE:
            answer.vote = F("vote") + VALUE
        elif vote == DOWNVOTE:
            answer.vote = F("vote") - VALUE

        answer.save(update_fields=["vote"])
        answer.refresh_from_db()
        return answer


class CommentSerializer(serializers.ModelSerializer):
    """Serializer class for a comment."""

    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = models.Comment
        fields = ("id", "comment", "created_by", "created_at", "updated_at")

    def create(self, validated_data):
        question_id = self.context.get(QUESTION, None)
        answer_id = self.context.get(ANSWER, None)
        if question_id:
            db_object = models.Question.objects.get(id=question_id)
        elif answer_id:
            db_object = models.Answer.objects.get(id=answer_id)

        comment = models.Comment.objects.create(
            content_object=db_object, **validated_data
        )
        return comment
