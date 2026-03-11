import datetime
from .email_service import send_maintenance_notification
from .sms_service import send_maintenance_sms


def simulate_maintenance_request():
    """
    Simulates a maintenance request trigger with mock data.
    
    This function demonstrates the notification workflow without 
    performing any database operations.
    
    TODO: Once the PostgreSQL migration is complete, this functionality 
    should be replaced by a post_save signal on the MaintenanceLog model.
    """
    
    # Mock data as per requirements
    mock_request_data = {
        'id': 1001,
        'lab': 'Computer Science Lab 1 (A-Block)',
        'issue_description': 'PC #14 Monitor is flickering and showing artifacts.',
        'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'technician_email': 'technician@lms-demo.com',  # Replace with actual email to test
        'technician_phone': '+1234567890',               # Replace with actual phone to test
    }
    
    print("--- SIMULATION STARTED ---")
    print(f"Triggering email for Request ID: {mock_request_data['id']}")
    send_maintenance_notification(mock_request_data)
    
    print(f"Triggering SMS for Request ID: {mock_request_data['id']}")
    send_maintenance_sms(mock_request_data)
    
    print("--- SIMULATION FINISHED ---")

if __name__ == "__main__":
    # Note: Running this script directly requires setting up the Django environment 
    # (DJANGO_SETTINGS_MODULE) or running it through 'python manage.py shell'.
    pass
