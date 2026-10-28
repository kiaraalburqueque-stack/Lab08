from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from quiz.views import ExamViewSet, OptionViewSet, QuestionViewSet

router = DefaultRouter()
router.register("exams", ExamViewSet)
router.register("questions", QuestionViewSet)
router.register("options", OptionViewSet)
urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
