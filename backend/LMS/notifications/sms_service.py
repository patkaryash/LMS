from django.conf import settings
from twilio.rest import Client


def _get_twilio_client():
    """Return a configured Twilio client using settings."""
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    return Client(account_sid, auth_token)


def send_maintenance_sms(request_data):
    """
    Sends an SMS notification for a maintenance request.

    This is a prototype implementation that mirrors email_service.py.
    It will later be connected to a Django post_save signal.

    Args:
        request_data (dict): Dictionary containing:
            - id: Request ID
            - lab: Lab Name/ID
            - issue_description: Details of the issue
            - created_at: Timestamp
            - technician_phone: Recipient phone number (E.164 format, e.g. +1234567890)
    """
    body = (
        f"LMS Maintenance Alert\n"
        f"Request #{request_data['id']} - {request_data['lab']}\n"
        f"Issue: {request_data['issue_description']}\n"
        f"Created: {request_data['created_at']}\n"
        f"Please attend to this ASAP."
    )

    from_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
    to_phone = request_data['technician_phone']

    # Console mode for development — just print instead of sending
    sms_backend = getattr(settings, 'SMS_BACKEND', 'console')
    if sms_backend == 'console':
        print(f"--- SMS (console mode) ---")
        print(f"FROM: {from_phone}")
        print(f"TO:   {to_phone}")
        print(f"BODY:\n{body}")
        print(f"--- END SMS ---")
        return True

    # Production mode — send via Twilio
    print(f"DEBUG: Attempting to send SMS to {to_phone}...")

    client = _get_twilio_client()
    message = client.messages.create(
        body=body,
        from_=from_phone,
        to=to_phone,
    )

    if message.sid:
        print(f"SUCCESS: SMS sent for Request #{request_data['id']} (SID: {message.sid})")
        return True
    else:
        print(f"FAILURE: SMS could not be sent for Request #{request_data['id']}")
        return False


def send_sms(to_phone, body):
    """
    Generic SMS sender. Use this for any ad-hoc SMS notification.

    Args:
        to_phone (str): Recipient phone number in E.164 format (e.g. +1234567890)
        body (str): The message text (max 1600 chars for Twilio)
    """
    from_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

    sms_backend = getattr(settings, 'SMS_BACKEND', 'console')
    if sms_backend == 'console':
        print(f"--- SMS (console mode) ---")
        print(f"FROM: {from_phone}")
        print(f"TO:   {to_phone}")
        print(f"BODY:\n{body}")
        print(f"--- END SMS ---")
        return True

    client = _get_twilio_client()
    message = client.messages.create(
        body=body,
        from_=from_phone,
        to=to_phone,
    )
    return bool(message.sid)
