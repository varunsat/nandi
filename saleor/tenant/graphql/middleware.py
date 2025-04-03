from django.db import connection
from graphql import GraphQLError
from ..utils import get_tenant_domain_from_request

class TenantMiddleware:
    def resolve(self, next, root, info, **args):
        request = info.context
        
        # Skip tenant check for introspection queries
        if info.field_name.lower() == '__schema':
            return next(root, info, **args)
            
        # Get tenant from request (set by TenantMiddleware)
        tenant = getattr(request, 'tenant', None)
        
        if not tenant and not request.path.startswith('/dashboard/'):
            raise GraphQLError('Invalid tenant domain')
            
        # Set tenant in connection for database operations
        connection.tenant = tenant
        
        try:
            return next(root, info, **args)
        finally:
            # Clear tenant from connection after operation
            if hasattr(connection, 'tenant'):
                del connection.tenant 