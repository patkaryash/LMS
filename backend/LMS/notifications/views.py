from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from . import services


class NotificationList(generics.ListAPIView):
    """GET /api/notifications/ — list all notifications for the logged-in user."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return services.get_notifications_for_user(self.request.user.id)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    """PATCH /api/notifications/<id>/read/ — mark a single notification as read."""
    updated = services.mark_as_read(pk, request.user.id)
    if not updated:
        return Response({'detail': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'detail': 'Notification marked as read.'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """PATCH /api/notifications/read-all/ — mark all notifications as read."""
    count = services.mark_all_as_read(request.user.id)
    return Response({'detail': f'{count} notification(s) marked as read.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """GET /api/notifications/unread-count/ — return unread notification count."""
    count = services.get_unread_count(request.user.id)
    return Response({'unread_count': count})
