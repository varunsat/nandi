from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='owned_tenants')
    
    # Branding
    logo = models.ImageField(upload_to='tenant_logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, null=True, blank=True)
    secondary_color = models.CharField(max_length=7, null=True, blank=True)
    
    # Contact Info
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    
    def clean(self):
        if self.subdomain:
            self.subdomain = self.subdomain.lower()
            if not self.subdomain.isalnum():
                raise ValidationError("Subdomain can only contain alphanumeric characters")
    
    def save(self, *args, **kwargs):
        if not self.subdomain:
            self.subdomain = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.subdomain})"

class TenantUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'tenant')
    
    def __str__(self):
        return f"{self.user.email} - {self.tenant.name}"

class TenantSettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='settings')
    enable_customer_accounts = models.BooleanField(default=True)
    enable_guest_checkout = models.BooleanField(default=True)
    default_currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    email_sender_name = models.CharField(max_length=100, null=True, blank=True)
    email_sender_address = models.EmailField(null=True, blank=True)
    
    def __str__(self):
        return f"Settings for {self.tenant.name}" 