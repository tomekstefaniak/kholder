from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Delete admin user"

    def handle(self, *args, **options):
        User = get_user_model()

        admin = User.objects.filter(username="admin").first()
        
        if not admin:
            self.stdout.write(self.style.WARNING("Admin user does not exist."))
            return

        admin.delete()

        self.stdout.write(self.style.SUCCESS("Admin user deleted successfully."))
