from django.test import TestCase
from django.db.utils import IntegrityError
from batch_priority.models import Bay


class BayModelTestCase(TestCase):
    def test_create_bay(self):
        # create a new bay
        bay = Bay.objects.create(name="Test Bay")

        self.assertEqual(Bay.objects.count(), 1)
        saved_bay = Bay.objects.get(pk=bay.pk)
        self.assertEqual(saved_bay.name, "Test Bay")

    def test_unique_bay_name(self):
        # test name is unique
        Bay.objects.create(name="Test Bay")
        with self.assertRaises(IntegrityError):
            Bay.objects.create(name="Test Bay")
