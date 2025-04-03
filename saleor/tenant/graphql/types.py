import graphene
from graphene_django import DjangoObjectType
from ..models import Tenant, TenantSettings, TenantUser

class TenantType(DjangoObjectType):
    class Meta:
        model = Tenant
        fields = (
            'id', 'name', 'subdomain', 'domain', 'created_at', 'is_active',
            'logo', 'primary_color', 'secondary_color', 'contact_email',
            'contact_phone'
        )

class TenantSettingsType(DjangoObjectType):
    class Meta:
        model = TenantSettings
        fields = (
            'enable_customer_accounts', 'enable_guest_checkout',
            'default_currency', 'timezone', 'email_sender_name',
            'email_sender_address'
        )

class TenantUserType(DjangoObjectType):
    class Meta:
        model = TenantUser
        fields = ('user', 'tenant', 'is_admin', 'created_at')

class TenantQueries(graphene.ObjectType):
    current_tenant = graphene.Field(TenantType)
    tenant_settings = graphene.Field(TenantSettingsType)
    tenant_users = graphene.List(TenantUserType)
    
    def resolve_current_tenant(self, info):
        return getattr(info.context, 'tenant', None)
    
    def resolve_tenant_settings(self, info):
        tenant = getattr(info.context, 'tenant', None)
        if tenant:
            return TenantSettings.objects.get(tenant=tenant)
        return None
    
    def resolve_tenant_users(self, info):
        tenant = getattr(info.context, 'tenant', None)
        if tenant:
            return TenantUser.objects.filter(tenant=tenant)
        return []

class CreateTenantInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    subdomain = graphene.String(required=True)
    domain = graphene.String()
    contact_email = graphene.String(required=True)
    contact_phone = graphene.String()
    primary_color = graphene.String()
    secondary_color = graphene.String()

class CreateTenant(graphene.Mutation):
    class Arguments:
        input = CreateTenantInput(required=True)
    
    tenant = graphene.Field(TenantType)
    
    @classmethod
    def mutate(cls, root, info, input):
        if not info.context.user.is_superuser:
            raise Exception("Only superusers can create tenants")
        
        tenant = Tenant.objects.create(
            name=input.name,
            subdomain=input.subdomain,
            domain=input.domain,
            contact_email=input.contact_email,
            contact_phone=input.contact_phone,
            primary_color=input.primary_color,
            secondary_color=input.secondary_color,
            owner=info.context.user
        )
        
        # Create default settings
        TenantSettings.objects.create(tenant=tenant)
        
        # Create tenant user for owner
        TenantUser.objects.create(
            user=info.context.user,
            tenant=tenant,
            is_admin=True
        )
        
        return CreateTenant(tenant=tenant)

class TenantMutations(graphene.ObjectType):
    create_tenant = CreateTenant.Field() 