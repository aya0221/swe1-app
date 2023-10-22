from django.test import TestCase
from django.utils import timezone
from .models import Question, Choice
from django.urls import reverse


def create_question(question_text, days):
    time = timezone.now() + timezone.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class SimpleModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - timezone.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])


class VoteViewTests(TestCase):
    def test_vote_view(self):
        question = create_question(question_text="Past Question.", days=-5)
        choice = Choice.objects.create(question=question, choice_text="Choice 1")
        url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(url, {"choice": choice.id})
        self.assertEqual(response.status_code, 302)  # redirect checking
        self.assertEqual(
            Choice.objects.get(id=choice.id).votes, 1
        )  # vote count checking


class IndexViewTest(TestCase):
    def test_index_view_with_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_index_view_with_a_past_question(self):
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"], ["<Question: Past question.>"]
        )
