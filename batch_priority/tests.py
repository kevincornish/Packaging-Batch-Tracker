from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Batch, Bay, Product, TargetDate


class BatchViewsTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        # Create product
        self.product = Product.objects.create(
            product_code="P001",
            product="Test Product",
            presentation="Test Presentation",
        )
        # Create bay
        self.bay = Bay.objects.create(name="Test Bay")
        # Create batch
        self.batch = Batch.objects.create(
            batch_number="B001",
            product_code=self.product,
            manufacture_date="2023-01-01",
            complete_date_target="2023-01-10",
            on_hold=False,
            bom_received=True,
            samples_received=True,
            batch_complete=False,
            production_check=False,
            assigned_to=self.user,
            created_by=self.user,
            last_modified_by=self.user,
        )
        # Create test bay
        self.target_date = TargetDate.objects.create(
            batch=self.batch,
            bay=self.bay,
            target_start_date="2024-01-02",
            target_end_date="2024-01-03",
        )

    def test_batch_list_view(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("batch_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "B001")

    def test_batch_detail_view(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("batch_detail", args=[self.batch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "B001")
        self.assertContains(response, "Test Product")

    def test_comment_creation(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("batch_detail", args=[self.batch.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("batch_detail", args=[self.batch.id]), {"text": "Test comment text"}
        )
        response = self.client.get(reverse("batch_detail", args=[self.batch.id]))
        self.assertContains(response, "Test comment text")

    def test_batch_history_view(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("batch_history", args=[self.batch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Batch History")
        self.assertContains(response, f"{self.batch.batch_number}")
