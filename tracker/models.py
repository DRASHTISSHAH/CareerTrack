from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date

STATUS_CHOICES = [
    ('Wishlist',   'Wishlist'),
    ('Applied',    'Applied'),
    ('Interview',  'Interview'),
    ('Rejected',   'Rejected'),
    ('Offer',      'Offer'),
]

class Application(models.Model):
    # Link every application to the user who created it.
    # settings.AUTH_USER_MODEL = 'auth.User' (Django's built-in User).
    # null=True so existing DB rows (before auth was added) are not broken.
    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,   # Delete all apps when the user is deleted
        null=True,
        blank=True,
    )
    company      = models.CharField(max_length=100)
    role         = models.CharField(max_length=100)
    location     = models.CharField(max_length=100, blank=True)
    status       = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Applied')
    applied_date = models.DateField(default=date.today)
    job_url      = models.URLField(blank=True)
    notes        = models.TextField(blank=True)
    ai_suggestion = models.TextField(blank=True)
    ai_chat       = models.JSONField(default=list, blank=True)
    created_at   = models.DateTimeField(default=timezone.now, editable=False)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_date', '-created_at']

    def __str__(self):
        return f"{self.company} — {self.role}"