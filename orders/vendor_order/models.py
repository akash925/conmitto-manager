from django.db import models

from api.base.models import ColorType, Note, is_in_org, is_a_manager_or_admin, UserPermissions, \
    field_changed, ModelBaseWithOrgAndFiles, ModelBase, is_an_admin, is_in_order
from api.orders.materials.models import Material
from api.utils.dictionary import is_key_present
from api.utils.email import construct_and_send_email


class VendorOrderIssueComment(ModelBase):
    issue = models.ForeignKey('VendorOrderIssue', on_delete=models.CASCADE, related_name='issue_comments')
    author = models.ForeignKey('personnel.Personnel', on_delete=models.SET_NULL, related_name='vendor_issues',
                               null=True)
    description = models.TextField(blank=True, default="")


class VendorOrderIssue(ModelBase):
    order = models.ForeignKey('VendorOrder', on_delete=models.CASCADE, related_name='issues')
    is_active = models.BooleanField(default=True, null=True)
    description = models.TextField(blank=True, default="")
    relative_id = models.PositiveSmallIntegerField(blank=True, null=True)


class VendorOrderMaterialInstance(ModelBase):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='instance')
    order = models.ForeignKey('orders.VendorOrder', on_delete=models.CASCADE, related_name='materials')
    amount = models.PositiveIntegerField(default=1)
    added_by = models.ForeignKey('personnel.Personnel', on_delete=models.SET_NULL, blank=True, null=True)


class VendorOrderType(ColorType):
    org = models.ForeignKey('personnel.Org', on_delete=models.CASCADE, blank=True, null=True,
                            related_name='vendor_types')

    def has_object_read_permission(self, request):
        return is_in_org(self, request)

    def has_object_write_permission(self, request):
        return is_in_org(self, request)


class VendorOrderNote(Note):
    vendor_order = models.ForeignKey('VendorOrder', on_delete=models.CASCADE, related_name='notes')


class VendorOrder(ModelBaseWithOrgAndFiles):
    VENDOR_ORDER_CREATED = 1
    CLIENT_ADMIN_APPROVED = 2
    SERVICE_PROVIDER_ACCEPTED = 3
    CLIENT_ADMIN_ACCEPTED = 4
    VENDOR_ORDER_SCHEDULED = 5
    VENDOR_ORDER_STARTED = 6
    ASSETS_IN_TRANSIT = 7
    AT_VENDOR_SITE = 8
    VENDOR_ORDER_COMPLETED = 9
    VENDOR_ORDER_STATUS = (
        (VENDOR_ORDER_CREATED, 'Vendor Order Created'),
        (CLIENT_ADMIN_APPROVED, 'Client Admin Approved'),
        (SERVICE_PROVIDER_ACCEPTED, 'Service Provider Accepted'),
        (CLIENT_ADMIN_ACCEPTED, 'Client Admin Accepted'),
        (VENDOR_ORDER_SCHEDULED, 'Vendor Order Scheduled'),
        (VENDOR_ORDER_STARTED, 'Vendor Order Started'),
        (ASSETS_IN_TRANSIT, 'Assets In Transit'),
        (AT_VENDOR_SITE, 'At Vendor Site'),
        (VENDOR_ORDER_COMPLETED, 'Vendor Order Completed'),
    )
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='vendor_orders')
    title = models.CharField(max_length=100, blank=True)
    stockroom_asset = models.ForeignKey('assets.StockroomAsset', on_delete=models.CASCADE, blank=True, null=True,
                                        related_name='vendor_orders')
    personnel = models.ForeignKey('personnel.Personnel', on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name='vendor_order_history')
    date = models.DateField(blank=True, null=True)
    inspection_note = models.TextField(blank=True, default="")
    status = models.PositiveIntegerField(choices=VENDOR_ORDER_STATUS, blank=True, null=True)
    email_sent = models.BooleanField(default=False, null=True)
    is_on_site = models.BooleanField(null=True)
    service_org = models.ForeignKey('personnel.Org', on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='vendor_orders')

    type = models.ForeignKey('VendorOrderType', on_delete=models.SET_NULL, related_name='orders', blank=True, null=True)

    @staticmethod
    def send_pending_email(vendor_order, request):
        asset = vendor_order.asset
        vendor_history = VendorOrder.objects.filter(asset=asset)

        asset_name = asset.name if asset.name else 'Unnamed Asset'

        return construct_and_send_email('support@conmitto.io',
                                        'Conmitto Support <support@conmitto.io>',
                                        'Vendor Order Created for ' + asset_name,
                                        'email/vendor_order.html',
                                        request,
                                        {
                                            'vendor_order': vendor_order,
                                            'stockroom_asset': vendor_order.stockroom_asset,
                                            'personnel': vendor_order.created_by,
                                            'org': vendor_order.org,
                                            'asset': vendor_order.asset,
                                            'vendor_history': vendor_history
                                        })

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_write_permission(self, request):
        if request.user.id and (is_in_org(self, request) or is_in_order(self, request)):
            if request.user.user_type >= UserPermissions.LEAD:
                # Handles the case where data is just being read
                if not request.data:
                    return False
                # Only allow editing inspection_note and materials
                if not set(request.data.keys()).difference({'materials'}):
                    if 'materials' in request.data:
                        for mat in request.data['materials']:
                            # Allow everyone to add materials to an order
                            if 'amount' not in mat or int(mat['amount']) > 0:
                                return True
                            # Only let managers/admins remove materials, unless the user removing it
                            # is the user that added it
                            else:
                                match = VendorOrderMaterialInstance.objects.filter(material_id=mat['id'],
                                                                                   order_id=self,
                                                                                   added_by=request.user.personnel)
                                return request.user.user_type <= UserPermissions.MANAGER or match
            if not is_a_manager_or_admin(request):
                if field_changed(self, request, 'status'):
                    return False
            # Once the order is complete don't allow edits
            if self.status == self.VENDOR_ORDER_COMPLETED:
                return False
            if field_changed(self, request, 'status'):
                if is_an_admin(request):
                    # While the order still needs approval, allow anyone to edit it
                    if self.status == self.VENDOR_ORDER_CREATED:
                        return True
                    # Only allow the order service provider admin advance this stage
                    elif self.status == self.CLIENT_ADMIN_APPROVED:
                        return is_in_order(self, request)
                    # Only allow org admin advance this stage
                    elif self.status == self.SERVICE_PROVIDER_ACCEPTED:
                        return is_in_org(self, request)
                    # Only allow the order service provider admin advance this stage
                    elif self.status == self.CLIENT_ADMIN_ACCEPTED:
                        return is_in_order(self, request)
                    # Allow either service provider admin or org admin advance the status
                    elif self.status == self.VENDOR_ORDER_SCHEDULED:
                        return is_in_org(self, request) or is_in_order(self, request)
                    # Only allow the order service provider admin advance this stage for onsite orders
                    elif self.status == self.VENDOR_ORDER_STARTED and self.is_on_site:
                        return is_in_order(self, request)
                    # Only allow org admin advance this stage for offsite orders
                    elif self.status == self.VENDOR_ORDER_STARTED and not self.is_on_site:
                        return is_in_org(self, request)
                    # Only allow the order service provider admin advance this stage
                    elif self.status == self.ASSETS_IN_TRANSIT:
                        return is_in_order(self, request)
                    # Only allow the order service provider admin advance this stage
                    elif self.status == self.AT_VENDOR_SITE:
                        return is_in_order(self, request)
            if is_key_present('issue', request.data):
                # Allow both service provider and client to add comments to an issue
                if is_key_present('comment', request.data['issue']):
                    return is_in_order(self, request) or is_in_org(self, request)
                # Only allow service providers to report an issue
                else:
                    return is_in_order(self, request)
            else:
                return is_in_org(self, request)
        return False

    @staticmethod
    def has_create_permission(request):
        return True
