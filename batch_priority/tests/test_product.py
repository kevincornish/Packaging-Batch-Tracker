from django.test import TestCase
from django.db.utils import IntegrityError
from batch_priority.models import Product

class ProductModelTestCase(TestCase):
    def test_create_product(self):
        # creating a new product
        product = Product.objects.create(
            product_code="P001",
            product="Test Product",
            presentation="Test Presentation"
        )

        self.assertEqual(Product.objects.count(), 1)
        saved_product = Product.objects.get(pk=product.pk)
        self.assertEqual(saved_product.product_code, "P001")
        self.assertEqual(saved_product.product, "Test Product")
        self.assertEqual(saved_product.presentation, "Test Presentation")

    def test_unique_product_code(self):
        # test product_code is unique
        Product.objects.create(
            product_code="P001",
            product="Test Product",
            presentation="Test Presentation"
        )
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                product_code="P001",
                product="Another Product",
                presentation="Another Presentation"
            )