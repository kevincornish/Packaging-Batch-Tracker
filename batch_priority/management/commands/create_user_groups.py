from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.conf import settings


class Command(BaseCommand):
    help = "Create user groups based on the USER_GROUPS setting in the .env file."

    def handle(self, *args, **options):
        user_groups = getattr(settings, "USER_GROUPS", None)

        if user_groups:
            groups = user_groups.split(",")

            for group_name in groups:
                group, created = Group.objects.get_or_create(name=group_name)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Group "{group}" created successfully.')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Group "{group}" already exists.')
                    )
        else:
            self.stdout.write(
                self.style.ERROR("USER_GROUPS setting not found in the .env file.")
            )
