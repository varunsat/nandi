from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.shortcuts import redirect
from .models import Tenant
from .utils import get_tenant_domain_from_request

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip tenant resolution for static and media files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Get domain/subdomain from request
        domain = get_tenant_domain_from_request(request)
        
        # Handle superadmin/marketplace admin routes
        if domain == settings.MARKETPLACE_ADMIN_DOMAIN:
            request.tenant = None
            return self.get_response(request)
        
        try:
            # Try to find tenant by domain first, then subdomain
            tenant = Tenant.objects.filter(domain=domain).first()
            if not tenant:
                subdomain = domain.split('.')[0]
                tenant = Tenant.objects.get(subdomain=subdomain)
            
            if not tenant.is_active:
                raise Http404("This store is currently inactive")
            
            # Attach tenant to request
            request.tenant = tenant
            
        except Tenant.DoesNotExist:
            # Redirect to marketplace homepage if no tenant found
            if settings.DEBUG:
                # In development, allow accessing without tenant
                request.tenant = None
                return self.get_response(request)
            return redirect(settings.MARKETPLACE_HOMEPAGE_URL)
        
        response = self.get_response(request)
        return response 