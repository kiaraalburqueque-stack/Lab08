from django.contrib import admin
from .models import Exam, Option, Question

admin.site.register([Exam, Question, Option])
