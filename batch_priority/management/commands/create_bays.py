from django.core.management.base import BaseCommand
from batch_priority.models import Bay
from django.conf import settings


class Command(BaseCommand):
    help = "Create bays / lines based on the BAYS setting in the .env file."

    def handle(self, *args, **options):
        bays = getattr(settings, "BAYS", None)

        if bays:
            bays = bays.split(",")

            for bay_name in bays:
                bay, created = Bay.objects.get_or_create(name=bay_name)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Bay "{bay}" created successfully.')
                    )
                else:
                    self.stdout.write(self.style.ERROR(f'Bay "{bay}" already exists.'))
        else:
            self.stdout.write(
                self.style.ERROR("BAYS setting not found in the .env file.")
            )
