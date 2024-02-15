from django.core.management.base import BaseCommand
from batch_priority.models import Product
from faker import Faker


class Command(BaseCommand):
    help = "Create test products."

    def handle(self, *args, **options):
        fake = Faker()

        # Generate a specified number of test products
        num_products = 10

        for _ in range(num_products):
            product_code = fake.unique.word()
            product = fake.word()
            presentation = fake.word()

            # Create the Product object
            product_obj, created = Product.objects.get_or_create(
                product_code=product_code,
                defaults={"product": product, "presentation": presentation},
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Product "{product_obj}" created successfully.')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Product "{product_obj}" already exists.')
                )
