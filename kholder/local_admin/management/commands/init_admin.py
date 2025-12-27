from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import getpass


class Command(BaseCommand):
    help = "Initialize admin user"

    def handle(self, *args, **options):
        User = get_user_model()

        if User.objects.filter(username="admin").exists():
            self.stdout.write(self.style.WARNING("Admin already exists"))
            return

        password = ""
        while True:
            password = getpass.getpass("Enter password for admin user: ").strip()
            password_confirm = getpass.getpass("Confirm password: ").strip()
            if password != password_confirm:
                self.stdout.write(self.style.ERROR("Passwords do not match. Please try again."))
            elif password == "":
                self.stdout.write(self.style.ERROR("Password cannot be empty. Please try again."))
            else:
                break

        User.objects.create_superuser(
            username="admin",
            password=password,
        )

        self.stdout.write(self.style.SUCCESS("Admin created"))
