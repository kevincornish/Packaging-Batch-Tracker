import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from django.contrib.auth.models import User
from batch_priority.models import Batch, Bay, Product, TargetDate, Comment

fake = Faker()


class Command(BaseCommand):
    help = "Generate random batches for testing"

    def add_arguments(self, parser):
        parser.add_argument("count", type=int, help="Number of batches to generate")

    def handle(self, *args, **options):
        count = options["count"]
        bays = Bay.objects.all()

        for _ in range(count):
            unique_batch_number = None
            while not unique_batch_number:
                potential_batch_number = fake.unique.random_number()
                if not Batch.objects.filter(
                    batch_number=potential_batch_number
                ).exists():
                    unique_batch_number = potential_batch_number

            is_batch_complete = random.choices([True, False], weights=[0.1, 0.9])[0]
            if is_batch_complete:
                is_production_check = fake.boolean()
            else:
                is_production_check = False

            batch = Batch(
                batch_number=unique_batch_number,
                product_code=random.choice(Product.objects.all()),
                manufacture_date=fake.date_this_year(),
                complete_date_target=fake.future_date(),
                on_hold=fake.boolean(),
                notes=fake.text(),
                bom_received=fake.boolean(),
                samples_received=fake.boolean(),
                batch_complete=is_batch_complete,
                batch_complete_date=timezone.now() if is_batch_complete else None,
                completed_by=(
                    random.choice(User.objects.all()) if is_batch_complete else None
                ),
                production_check=is_production_check,
                production_check_date=timezone.now() if is_production_check else None,
                production_checked_by=(
                    random.choice(User.objects.all()) if is_production_check else None
                ),
                assigned_to=random.choice(User.objects.all()),
                created_by=random.choice(User.objects.all()),
                last_modified_by=random.choice(User.objects.all()),
            )

            batch.save()

            selected_bays = random.sample(list(bays), random.randint(1, len(bays)))

            # Create TargetDates related to the batch
            for bay in selected_bays:
                TargetDate.objects.create(
                    batch=batch,
                    bay=bay,
                    target_start_date=fake.date_this_year(),
                    target_end_date=fake.future_date(),
                )

            # Create comments (between 10-20) for each batch
            comment_count = random.randint(10, 20)
            for _ in range(comment_count):
                Comment.objects.create(
                    batch=batch,
                    user=random.choice(User.objects.all()),
                    timestamp=timezone.now(),
                    text=fake.text(),
                )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully generated {count} random batches.")
        )
