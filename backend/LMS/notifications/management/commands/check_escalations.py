from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from labs.models import MaintenanceLog, User
from notifications.models import Notification
from notifications.services import create_notification


class Command(BaseCommand):
    help = 'Check for unresolved maintenance logs older than 7 days and create escalation notifications for admin users.'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(days=7)

        # Find all pending maintenance logs reported more than 7 days ago
        stale_logs = MaintenanceLog.objects.filter(
            status='pending',
            reported_on__lte=threshold,
        )

        if not stale_logs.exists():
            self.stdout.write('No stale maintenance logs found.')
            return

        # Get admin users to notify (project has no lab_assistant role)
        admin_users = User.objects.filter(role='admin', is_active=True)
        if not admin_users.exists():
            self.stdout.write('No active admin users to notify.')
            return

        created_count = 0
        for log in stale_logs:
            for admin in admin_users:
                # Prevent duplicate: skip if an escalation notification already
                # exists for this (user, maintenance_log) pair
                already_sent = Notification.objects.filter(
                    user=admin,
                    maintenance_log=log,
                    type='escalation',
                ).exists()
                if already_sent:
                    continue

                days_old = (timezone.now() - log.reported_on).days
                message = (
                    f'Maintenance issue on {log.equipment} (Lab: {log.lab}) '
                    f'has been pending for {days_old} days. '
                    f'Reported by {log.reported_by or "unknown"}.'
                )
                create_notification(
                    user_id=admin.id,
                    maintenance_log_id=log.id,
                    message=message,
                    notification_type='escalation',
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Escalation check complete. {created_count} notification(s) created.'
        ))
