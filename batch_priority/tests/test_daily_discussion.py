from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime
from batch_priority.models import DailyDiscussion, DailyDiscussionComment


class DailyDiscussionTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )

        # Create a daily discussion
        self.discussion_date = datetime.now().date()
        self.discussion = DailyDiscussion.objects.create(date=self.discussion_date)

    def test_view_daily_discussion(self):
        response = self.client.get(
            reverse("daily_discussion", args=[str(self.discussion_date)])
        )
        self.assertEqual(response.status_code, 200)

    def test_add_comment(self):
        self.client.login(username="testuser", password="testpassword")

        comment_text = "This is a test comment."
        response = self.client.post(
            reverse("daily_discussion", args=[str(self.discussion_date)]),
            {"discussion": self.discussion_date, "text": comment_text},
        )
        response = self.client.get(
            reverse("daily_discussion", args=[str(self.discussion_date)])
        )
        self.assertContains(response, comment_text)

    def test_edit_comment(self):
        # Create a comment by the test user
        comment = DailyDiscussionComment.objects.create(
            discussion=self.discussion, user=self.user, text="Original comment text."
        )

        # attempt to edit the comment as another user (should fail)
        self.client.login(username="otheruser", password="otherpassword")
        response = self.client.get(
            reverse("edit_discussion_comment", args=[comment.id])
        )

        # unauthorized user redirected
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("daily_discussion"))

        # edit the comment as the original user (should succeed)
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(
            reverse("edit_discussion_comment", args=[comment.id])
        )

        self.assertEqual(response.status_code, 200)
