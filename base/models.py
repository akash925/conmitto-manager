import re
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField

DEFAULT_COLOR_TYPE_COLOR = "#2c3655"

# A base set of fields to ignore for HistoricalRecords fields
BASE_HISTORY_IGNORE_FIELDS = ['created_at', 'updated_at', 'created_by']


class UserPermissions:
    """
    Contains the different permission levels that a user can have
    """
    ADMIN = 1
    MANAGER = 2
    LEAD = 3
    TECHNICIAN = 4
    CONTRACTOR = 5
    SERVICE_PROVIDER = 6


def validate_color(value):
    """
    Validates an RBG hexadecimal color code
    :param str value: The hex color code
    :raises ValidationError: If the value is not a valid color
    """
    if not re.match('^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise ValidationError(
            _('%(value)s is not a valid color string'),
            params={'value': value},
        )


def is_in_org(obj, request):
    """
    Check if the user in the request belongs to the same organization as the specified object
    :param obj: The Django model to look at
    :param request: The request object
    :return:
    """
    user = request.user
    return user.id and user.personnel and obj.org == user.personnel.default_org


def is_in_order(obj, request):
    """
    Check if the user's org id is equal to the vendor order service provider org id,
    and check if the request is meant to update the status or raise an issue
    """
    user = request.user
    if user.id and user.personnel and obj.service_org == user.personnel.default_org:
        return 'status' in request.data or 'issue' in request.data
    return False


def is_an_admin(request):
    """
    Check if the user in the request is an admin
    :param request: The request object
    """
    return request.user.id and request.user.user_type <= UserPermissions.ADMIN


def is_a_manager_or_admin(request):
    """
    Check if the user in the request is a manager or an admin
    :param request: The request object
    """
    return request.user.id and request.user.user_type <= UserPermissions.MANAGER


def created_this_object(obj, request):
    """
    Check if the object that is provided was created by the user in the request
    :param obj: The Django model to look at
    :param request: The request object
    """
    return obj.created_by.user == request.user


def field_changed(obj, request, field_name, is_foreign_key=False):
    obj_field = getattr(obj, field_name)
    if is_foreign_key and obj_field:
        obj_field = obj_field.id
    return field_name in request.data and request.data[field_name] != obj_field


def fields_changed(obj, request, field_names, is_foreign_key=False):
    """
    Checks if any of the fields in the request changed
    """
    for field in field_names:
        if field_changed(obj, request, field, is_foreign_key):
            return True
    return False


class ModelBase(models.Model):
    """
    Includes the following fields:
     * created_at
     * updated_at
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @staticmethod
    def has_read_permission(request):
        return True


class ModelBaseWithOrg(ModelBase):
    """
    Includes the following fields:
     * created_at
     * updated_at
     * created_by
     * org
    """
    created_by = models.ForeignKey('personnel.Personnel', on_delete=models.SET_NULL, blank=True, null=True)
    org = models.ForeignKey('personnel.Org', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class ModelBaseWithOrgAndFiles(ModelBaseWithOrg):
    """
    Includes the following fields:
     * created_at
     * updated_at
     * created_by
     * org
     * display_image
     * warranty_document
     * UUID
    """
    display_image = models.CharField(max_length=1000, blank=True, validators=[URLValidator()])
    warranty_document = models.CharField(max_length=1000, blank=True, validators=[URLValidator()])
    UUID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class ModelWithBarcode(models.Model):
    """
    A model with a barcode field
    """
    barcode = models.OneToOneField("barcodes.Barcode", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        abstract = True


class Note(ModelBase):
    """
    The base class for a Note
    """
    content = models.TextField()
    created_by = models.ForeignKey('personnel.Personnel', on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True

    def has_object_read_permission(self, request):
        return request.user.id and self.created_by.default_org == request.user.personnel.default_org

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_write_permission(self, request):
        # Make sure they are in their own org
        if request.user.id and self.created_by.default_org == request.user.personnel.default_org:
            return created_this_object(self, request)
        return False

    @staticmethod
    def has_create_permission(request):
        return True


class ColorType(ModelBase):
    """
    Base model for editable color dropdowns
    """
    name = models.CharField(max_length=300)
    color = models.CharField(max_length=7, validators=[validate_color])

    class Meta:
        abstract = True

    @staticmethod
    def has_write_permission(request):
        return is_a_manager_or_admin(request)


class Template(ModelBase):
    """
    The base class for templates, which are customizable fields that can be added to an object
    """
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    @staticmethod
    def has_write_permission(request):
        return is_a_manager_or_admin(request)


class TemplateField(ModelBase):
    """
    The base class for a field within a template. Think of this as a key in a dictionary
    """
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, blank=True, default='input')
    units = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

    @staticmethod
    def has_write_permission(request):
        return is_a_manager_or_admin(request)


class TemplateData(ModelBase):
    """
    The base class for a value within a template. Think of this as a value in a dictionary
    """
    value = models.CharField(max_length=200, default='', blank=True)

    class Meta:
        abstract = True


class InventoryModel(ModelBaseWithOrgAndFiles, ModelWithBarcode):
    """Abstract model for materials and products."""
    name = models.CharField(max_length=1000, blank=True)
    manufacturer = models.CharField(max_length=1000, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    price = MoneyField(
        max_digits=9, decimal_places=2, blank=True, null=True,
        default_currency='USD')
    suppliers = models.ManyToManyField('warehouse.Supplier')

    def delete(self, **kwargs):
        if self.barcode:
            self.barcode.delete()
        return super(InventoryModel, self).delete(**kwargs)

    class Meta:
        abstract = True

    def has_object_read_permission(self, request):
        return is_in_org(self, request)

    @staticmethod
    def has_write_permission(request):
        return is_an_admin(request)

    def has_object_write_permission(self, request):
        return is_in_org(self, request)

    def __str__(self):
        return "%s" % self.name
