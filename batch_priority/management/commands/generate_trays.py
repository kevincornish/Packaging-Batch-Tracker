from django.core.management.base import BaseCommand
from batch_priority.models import Tray
from faker import Faker
import random


# Define the command class
class Command(BaseCommand):
    help = "Create fake trays."

    # Define the handle method
    def handle(self, *args, **options):
        fake = Faker()

        # Generate a specified number of fake trays
        num_trays = 10

        for _ in range(num_trays):
            tray_type = fake.unique.word()
            tray_size = fake.word()
            containers_per_tray = random.randint(100, 1000)

            # Create the Tray object
            tray_obj, created = Tray.objects.get_or_create(
                tray_type=tray_type,
                defaults={
                    "tray_size": tray_size,
                    "containers_per_tray": containers_per_tray,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tray "{tray_obj}" created successfully.')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Tray "{tray_obj}" already exists.')
                )
