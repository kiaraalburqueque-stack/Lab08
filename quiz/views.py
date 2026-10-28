from django.db import transaction
from rest_framework import filters, serializers, viewsets
from .models import Exam, Option, Question
from .serializers import ExamSerializer, OptionSerializer, QuestionSerializer


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related("exam").prefetch_related("options")
    serializer_class = QuestionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["text"]

    def get_queryset(self):
        queryset = super().get_queryset()
        exam = self.request.query_params.get("exam")
        if exam is not None:
            try:
                exam_id = int(exam)
                if exam_id < 1 or exam_id > 9223372036854775807:
                    raise ValueError
            except ValueError:
                raise serializers.ValidationError({"exam": "Use a positive integer."})
            queryset = queryset.filter(exam_id=exam_id)
        return queryset


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.select_related("question")
    serializer_class = OptionSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        question = serializer.validated_data["question"]
        Question.objects.select_for_update().get(pk=question.pk)
        serializer.validate(serializer.validated_data)
        serializer.save()

    @transaction.atomic
    def perform_update(self, serializer):
        Question.objects.select_for_update().get(pk=serializer.instance.question_id)
        serializer.instance.refresh_from_db()
        serializer.validate(serializer.validated_data)
        serializer.save()

    @transaction.atomic
    def perform_destroy(self, instance):
        Question.objects.select_for_update().get(pk=instance.question_id)
        instance.refresh_from_db()
        if instance.is_correct:
            raise serializers.ValidationError({
                "is_correct": "Cannot delete the correct option. "
                "Replace the question's nested options first."
            })
        instance.delete()
