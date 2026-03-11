from .models import Notification
from labs.models import User


def create_notification(user_id, maintenance_log_id, message, notification_type='info'):
    """Create a notification for a specific user linked to a maintenance log."""
    return Notification.objects.create(
        user_id=user_id,
        maintenance_log_id=maintenance_log_id,
        type=notification_type,
        message=message,
    )


def get_notifications_for_user(user_id):
    """Return all notifications for a user, ordered by most recent first."""
    return Notification.objects.filter(user_id=user_id)


def mark_as_read(notification_id, user_id):
    """Mark a single notification as read. Returns True if updated, False if not found."""
    updated = Notification.objects.filter(id=notification_id, user_id=user_id).update(is_read=True)
    return updated > 0


def mark_all_as_read(user_id):
    """Mark all unread notifications for a user as read. Returns count of updated rows."""
    return Notification.objects.filter(user_id=user_id, is_read=False).update(is_read=True)


def get_unread_count(user_id):
    """Return the count of unread notifications for a user."""
    return Notification.objects.filter(user_id=user_id, is_read=False).count()
