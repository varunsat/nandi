from .utils import get_tenant_domain

def tenant(request):
    """
    Add tenant-related context to templates.
    """
    tenant = getattr(request, 'tenant', None)
    
    return {
        'tenant': tenant,
        'tenant_domain': get_tenant_domain(tenant, request) if tenant else None,
        'is_tenant_admin': (
            request.user.is_authenticated and
            tenant and
            tenant.tenantuser_set.filter(user=request.user, is_admin=True).exists()
        ),
    } 