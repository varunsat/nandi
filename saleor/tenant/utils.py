from django.conf import settings
from django.db import connection
from functools import wraps

def get_tenant_domain_from_request(request):
    """Extract tenant domain from request."""
    host = request.get_host().lower()
    if ':' in host:
        host = host.split(':')[0]
    return host

def tenant_context(tenant):
    """Decorator to set tenant context for a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Store current tenant
            current_tenant = getattr(connection, 'tenant', None)
            
            try:
                # Set new tenant
                connection.tenant = tenant
                return func(*args, **kwargs)
            finally:
                # Restore previous tenant
                connection.tenant = current_tenant
        return wrapper
    return decorator

def get_tenant_model():
    """Get the Tenant model."""
    from .models import Tenant
    return Tenant

def get_tenant_specific_table_name(model):
    """Get the table name for a model within tenant context."""
    if not hasattr(model, '_meta'):
        return model
    
    table_name = model._meta.db_table
    tenant_prefix = getattr(connection, 'tenant_prefix', '')
    
    if tenant_prefix and not table_name.startswith(tenant_prefix):
        return f"{tenant_prefix}{table_name}"
    return table_name

def get_tenant_specific_schema_name(tenant):
    """Get the schema name for a tenant."""
    return f"tenant_{tenant.id}"

def create_tenant_schema(tenant):
    """Create a new schema for tenant."""
    schema_name = get_tenant_specific_schema_name(tenant)
    with connection.cursor() as cursor:
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
    return schema_name

def get_tenant_domain(tenant, request=None):
    """Get the full domain for a tenant."""
    if tenant.domain:
        return tenant.domain
    
    if settings.DEBUG and request:
        return request.get_host()
        
    return f"{tenant.subdomain}.{settings.MARKETPLACE_DOMAIN}" 