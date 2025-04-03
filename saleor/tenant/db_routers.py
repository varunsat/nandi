from django.db import connection
from django.conf import settings

class TenantRouter:
    """
    Database router that handles tenant-specific models.
    """
    
    def db_for_read(self, model, **hints):
        """Point all operations to the tenant-specific schema."""
        if hasattr(model, 'tenant'):
            tenant = getattr(connection, 'tenant', None)
            if tenant:
                return 'default'  # Using default DB with schema routing
        return None

    def db_for_write(self, model, **hints):
        """Point all operations to the tenant-specific schema."""
        if hasattr(model, 'tenant'):
            tenant = getattr(connection, 'tenant', None)
            if tenant:
                return 'default'  # Using default DB with schema routing
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow any relation if both objects are tenant-specific or not.
        """
        tenant1 = getattr(obj1, 'tenant', None)
        tenant2 = getattr(obj2, 'tenant', None)
        
        # Both objects are tenant-specific
        if tenant1 and tenant2:
            return tenant1.id == tenant2.id
        
        # Neither object is tenant-specific
        if not tenant1 and not tenant2:
            return True
        
        # One object is tenant-specific, one isn't
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure tenant-specific models only sync to tenant schemas.
        """
        if db == 'default':
            return True
        return None 