from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from faker import Faker
import os
import random


class Command(BaseCommand):
    help = "Create test users."

    def add_arguments(self, parser):
        parser.add_argument("count", type=int, help="Number of users to generate")

    def handle(self, *args, **options):
        fake = Faker()
        email_domain = os.environ.get("EMAIL_DOMAIN")
        groups = Group.objects.all()

        # Generate a specified number of test users
        num_users = options["count"]

        for _ in range(num_users):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@{email_domain}"
            password = fake.password()

            # Create the User object
            user_obj, created = User.objects.get_or_create(
                username=f"{first_name.lower()}.{last_name.lower()}",
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user_obj.set_password(password)

            # Assign random groups to the user
            user_groups = random.sample(list(groups), random.randint(1, len(groups)))
            user_obj.groups.set(user_groups)
            user_obj.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'User "{email}" created successfully.')
                )
            else:
                self.stdout.write(self.style.ERROR(f'User "{email}" already exists.'))
