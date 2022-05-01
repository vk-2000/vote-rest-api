from rest_framework import serializers
from vote.models import Choice, Poll, Question


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ('id', 'name', 'result_public', 'active')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'desc',)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'text')


class ChoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'text', 'votes')


class QuestionDetailSerializer(serializers.ModelSerializer):
    choices = ChoiceDetailSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'desc', 'choices')


class PollDetailSerializer(serializers.ModelSerializer):
    questions = QuestionDetailSerializer(many=True)

    class Meta:
        model = Poll
        fields = ('id', 'name', 'host', 'result_public', 'active', 'questions')


class QuestionVoteSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'desc', 'choices')


class PollVoteSerializer(serializers.ModelSerializer):
    questions = QuestionVoteSerializer(many=True)

    class Meta:
        model = Poll
        fields = ('id', 'name', 'host', 'result_public', 'active', 'questions')
