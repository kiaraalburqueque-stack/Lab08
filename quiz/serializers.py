from django.db import transaction
from rest_framework import serializers
from .models import Exam, Option, Question


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["id", "title", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class NestedOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "is_correct"]
        read_only_fields = ["id"]


class QuestionSerializer(serializers.ModelSerializer):
    options = NestedOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "exam", "text", "options", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        options = attrs.get("options")
        if options is None and self.instance is None:
            raise serializers.ValidationError({"options": "This field is required."})
        if options is not None and sum(o.get("is_correct", False) for o in options) != 1:
            raise serializers.ValidationError({
                "options": "Exactly one option must be correct."
            })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        options = validated_data.pop("options")
        question = Question.objects.create(**validated_data)
        Option.objects.bulk_create([Option(question=question, **o) for o in options])
        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = Question.objects.select_for_update().get(pk=instance.pk)
        options = validated_data.pop("options", None)
        instance = super().update(instance, validated_data)
        if options is not None:
            instance.options.all().delete()
            Option.objects.bulk_create([Option(question=instance, **o) for o in options])
        return instance


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "question", "text", "is_correct"]
        read_only_fields = ["id"]
        validators = []

    def validate(self, attrs):
        instance = self.instance
        question = attrs.get("question", instance.question if instance else None)
        if instance and question.pk != instance.question_id:
            raise serializers.ValidationError({
                "question": "Moving an option to another question is not allowed."
            })
        if question is not None:
            correct = question.options.filter(is_correct=True)
            if instance:
                correct = correct.exclude(pk=instance.pk)
            total = correct.count() + int(attrs.get(
                "is_correct", instance.is_correct if instance else False
            ))
            if total != 1:
                raise serializers.ValidationError({
                    "is_correct": "Exactly one option must remain correct. "
                    "Replace the question's nested options to change the correct answer."
                })
        return attrs
