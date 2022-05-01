from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChoiceSerializer, PollSerializer, PollDetailSerializer, PollVoteSerializer, QuestionSerializer
from users.serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from vote.models import *
# Create your views here.


class IsHostPoll(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.host == request.user


class IsQuestionHost(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.poll.host == request.user


class IsChoiceHost(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.question.poll.host == request.user


class PollActive(permissions.BasePermission):
    message = {'message': 'Poll not live', 'error_code': 1}

    def has_object_permission(self, request, view, obj):
        return obj.active


class NotVoted(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        self.message = {'message': 'voted', 'error_code': 2}
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get(
            'REMOTE_ADDR', '')).split(',')[0].strip()
        return not obj.voted_ip_addresses.filter(ip_address=ip).exists()


class Register(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "user created"}, status=201)
        return Response(serializer.errors, status=400)


class PollListAdd(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        polls = Poll.objects.filter(host=request.user)
        serializer = PollSerializer(polls, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.user)
        serializer = PollSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class PollUpdateDelete(APIView):
    permission_classes = [IsAuthenticated, IsHostPoll]

    def patch(self, request, pk):
        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({"message": "Poll not found"}, status=404)
        self.check_object_permissions(request=request, obj=poll)
        serializer = PollSerializer(poll, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({"message": "Poll not found"}, status=404)
        self.check_object_permissions(request=request, obj=poll)
        poll.delete()
        return Response(status=204)


class QuestionInfo(APIView):
    permission_classes = [IsAuthenticated, IsQuestionHost]

    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=404)
        self.check_object_permissions(request=request, obj=question)
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=404)
        self.check_object_permissions(request=request, obj=question)
        serializer = QuestionSerializer(
            question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def post(self, request, pk):
        serializer = QuestionSerializer(data=request.data)
        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({'message': 'poll does not exist'}, status=404)
        if poll.host != request.user:
            raise PermissionDenied(detail='permission denied')
        if serializer.is_valid():
            serializer.save(poll=poll)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        question = Question.objects.get(pk=pk)
        self.check_object_permissions(request=request, obj=question)
        question.delete()
        return Response(status=204)


class ChoiceInfo(APIView):
    permission_classes = [IsAuthenticated, IsChoiceHost]

    def get(self, request, pk):
        try:
            choice = Choice.objects.get(pk=pk)
        except Choice.DoesNotExist:
            return Response({"message": "Choice not found"}, status=404)
        self.check_object_permissions(request=request, obj=choice)
        serializer = ChoiceSerializer(choice)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            choice = Choice.objects.get(pk=pk)
        except Choice.DoesNotExist:
            return Response({"message": "Choice not found"}, status=404)
        self.check_object_permissions(request=request, obj=choice)

        serializer = ChoiceSerializer(choice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)

    def post(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"message: Question not found"}, status=404)
        if question.poll.host != request.user:
            raise PermissionDenied(detail='permission denied')
        serializer = ChoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(question=question)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            choice = Choice.objects.get(pk=pk)
        except Choice.DoesNotExist:
            return Response({"message": "Choice not found"}, status=404)
        self.check_object_permissions(request=request, obj=choice)
        choice.delete()
        return Response(status=204)


class PollDetail(APIView):
    permission_classes = [IsAuthenticated, IsHostPoll]

    def get(self, request, pk):

        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({'message': 'poll does not exist'}, status=404)
        self.check_object_permissions(request=request, obj=poll)
        ser = PollDetailSerializer(poll)
        return Response(ser.data)


class Vote(APIView):
    authentication_classes = []
    permission_classes = [PollActive, NotVoted]

    def get(self, request, pk):
        print(self.get_permissions())
        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({'message': 'poll does not exist'}, status=404)
        self.check_object_permissions(request=request, obj=poll)
        serializer = PollVoteSerializer(poll)
        return Response(serializer.data)

    def post(self, request, pk):
        print(request.data)
        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({'message': 'poll does not exist'}, status=404)
        self.check_object_permissions(request=request, obj=poll)

        # check if all choices belong to the same poll
        for c in request.data.get('choices'):
            choice = Choice.objects.get(pk=int(c))
            if choice.question.poll != poll:
                return Response({"message": "invalid choice"}, status=400)

        # increment votes of all choices
        for c in request.data.get('choices'):
            choice = Choice.objects.get(pk=int(c))
            choice.votes += 1
            choice.save()

        # add ip address of voter to poll

        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get(
            'REMOTE_ADDR', '')).split(',')[0].strip()
        IpAddress.objects.create(ip_address=ip_address, poll=poll)

        return Response({"message": "Voted successfully"}, status=200)


class Result(APIView):
    def get(self, request, pk):
        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({'message': 'poll does not exist'}, status=404)
        if not poll.result_public:
            return Response({"message": "Result not available"}, status=403)
        serializer = PollDetailSerializer(poll)
        return Response(serializer.data)
