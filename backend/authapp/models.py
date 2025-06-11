from django.db import models

class LineUser(models.Model):
    line_sub = models.CharField(max_length=255, unique=True)  # LINEのユーザーID
    access_token = models.CharField(max_length=512, null=True, blank=True)
    refresh_token = models.CharField(max_length=512, null=True, blank=True)
    access_token_expire_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.line_sub})"