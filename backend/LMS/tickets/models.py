from django.db import models
from django.conf import settings

class Ticket(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    pc = models.ForeignKey('labs.PC', on_delete=models.CASCADE, related_name='tickets', null=True)
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=(('open','Open'),('in_progress','In Progress'),('resolved','Resolved')), default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Ticket #{self.id} - {self.pc.device_name} - {self.status}"
