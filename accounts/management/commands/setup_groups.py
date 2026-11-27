
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User


class Command(BaseCommand):
    help = "Creates user groups and assigns permissions."

    def handle(self, *args, **options):
        groups_permissions = {
            "Клиенти": [
                ("requests", "add_jobrequest"),
                ("requests", "view_jobrequest"),
                ("requests", "change_jobrequest"),
                ("offers", "view_offer"),
                ("services", "view_service"),
                ("services", "view_servicecategory"),
            ],
            "Майстори": [
                ("requests", "view_jobrequest"),
                ("offers", "add_offer"),
                ("offers", "view_offer"),
                ("services", "view_service"),
                ("services", "view_servicecategory"),
            ],
        }

        groups = {}

        for group_name, permission_list in groups_permissions.items():
            group, created = Group.objects.get_or_create(
                name=group_name
            )

            permissions = []

            for app_label, codename in permission_list:
                try:
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename,
                    )
                except Permission.DoesNotExist:
                    raise CommandError(
                        f"Permission not found: {app_label}.{codename}"
                    )

                permissions.append(permission)

            group.permissions.set(permissions)
            groups[group_name] = group

            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} group: {group_name}"
                )
            )

        # Assign existing users to their respective groups.
        for user in User.objects.all():
            if user.role == User.Role.CLIENT:
                group = groups["Клиенти"]
            elif user.role == User.Role.MASTER:
                group = groups["Майстори"]
            else:
                continue

            user.groups.add(group)

        self.stdout.write(
            self.style.SUCCESS(
                "Groups and user assignments completed."
            )
        )
