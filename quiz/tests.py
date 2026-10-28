from rest_framework.test import APITestCase
from .models import Exam, Question


class QuizAPITests(APITestCase):
    def setUp(self):
        self.exam = Exam.objects.create(title="Python")
        self.payload = {
            "exam": self.exam.pk, "text": "What is Django?",
            "options": [
                {"text": "A framework", "is_correct": True},
                {"text": "A database", "is_correct": False},
            ],
        }

    def create_question(self):
        response = self.client.post("/api/questions/", self.payload)
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_nested_create_and_partial_update(self):
        question = self.create_question()
        url = f"/api/questions/{question['id']}/"
        response = self.client.patch(url, {"text": "Updated"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["options"], question["options"])
        replacement = [{"text": "New correct", "is_correct": True}]
        response = self.client.patch(url, {"options": replacement})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["options"]), 1)

    def test_invalid_options_never_create_or_modify_question(self):
        for options in ([], [{"text": "No"}], [
            {"text": "Yes", "is_correct": True},
            {"text": "Also yes", "is_correct": True},
        ]):
            response = self.client.post(
                "/api/questions/", {**self.payload, "options": options}
            )
            self.assertEqual(response.status_code, 400)
        self.assertEqual(Question.objects.count(), 0)
        question = self.create_question()
        response = self.client.patch(
            f"/api/questions/{question['id']}/", {"text": "Changed", "options": []}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Question.objects.get().text, self.payload["text"])

    def test_option_endpoint_preserves_correct_answer(self):
        question = self.create_question()
        correct, incorrect = question["options"]
        for method, url, body in [
            ("post", "/api/options/", {
                "question": question["id"], "text": "Extra", "is_correct": True,
            }),
            ("patch", f"/api/options/{incorrect['id']}/", {"is_correct": True}),
            ("patch", f"/api/options/{correct['id']}/", {"is_correct": False}),
            ("delete", f"/api/options/{correct['id']}/", {}),
        ]:
            response = getattr(self.client, method)(url, body)
            self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(self.client.delete(
            f"/api/options/{incorrect['id']}/"
        ).status_code, 204)

    def test_relationship_changes_and_read_only_fields(self):
        question = self.create_question()
        other = self.create_question()
        response = self.client.patch(
            f"/api/options/{question['options'][0]['id']}/",
            {"question": other["id"]},
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(
            f"/api/questions/{question['id']}/", {"id": 999, "created_at": "bad"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], question["id"])

    def test_filter_search_pagination_and_errors(self):
        for _ in range(6):
            self.create_question()
        other = Exam.objects.create(title="Other")
        response = self.client.get(f"/api/questions/?exam={other.pk}")
        self.assertEqual(response.data["count"], 0)
        response = self.client.get("/api/questions/?search=Django")
        self.assertEqual(response.data["count"], 6)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])
        self.assertEqual(len(self.client.get(
            "/api/questions/?page=2"
        ).data["results"]), 1)
        for value in ("abc", "0", "-1", "9" * 30):
            self.assertEqual(self.client.get(
                f"/api/questions/?exam={value}"
            ).status_code, 400)
        self.assertEqual(self.client.post("/api/exams/", {}).status_code, 400)
        self.assertEqual(self.client.post(
            "/api/questions/", {**self.payload, "exam": "bad"}
        ).status_code, 400)
        self.assertEqual(self.client.get("/api/exams/99999/").status_code, 404)

    def test_exam_delete_cascades(self):
        self.create_question()
        self.assertEqual(self.client.delete(
            f"/api/exams/{self.exam.pk}/"
        ).status_code, 204)
        self.assertEqual(Question.objects.count(), 0)
