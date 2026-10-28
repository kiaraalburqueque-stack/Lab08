from django.core.management.base import BaseCommand
from django.db import transaction
from quiz.models import Exam, Option, Question


class Command(BaseCommand):
    help = "Create an idempotent sample exam with seven questions."

    @transaction.atomic
    def handle(self, *args, **options):
        exam, _ = Exam.objects.get_or_create(
            title="Django REST Framework demo",
            defaults={"description": "Seven questions to demonstrate pagination."},
        )
        for number in range(1, 8):
            question, created = Question.objects.get_or_create(
                exam=exam, text=f"Django {number}: which tool exposes a REST API?"
            )
            if created:
                Option.objects.bulk_create([
                    Option(question=question, text="Django REST Framework", is_correct=True),
                    Option(question=question, text="A spreadsheet", is_correct=False),
                ])
        self.stdout.write(self.style.SUCCESS(f"Demo ready. Exam ID: {exam.pk}"))
