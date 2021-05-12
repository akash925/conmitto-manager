import pytz
import six
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.locations.models import LocationInstance
from api.utils.permissions import DRYPermissionsScopeField


# https://github.com/rsinger86/drf-flex-fields
class BaseModelSerializer(FlexFieldsModelSerializer):
    created_at = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    updated_at = serializers.DateTimeField(allow_null=True, required=False, read_only=True)

    class Meta:
        abstract = True


class PermissionSerializerBase(BaseModelSerializer):
    # permissions = serializers.SerializerMethodField(method_name='get_permission_field')
    permissions = DRYPermissionsScopeField()

    class Meta:
        fields = ['permissions']

    # def get_permission_field(self, obj):
    #     # print('get permission self', self.__dict__)
    #     # if self.context:
    #
    #     return DRYPermissionsScopeField(self, obj)


class FilesModelSerializer(serializers.ModelSerializer):
    display_image = serializers.SerializerMethodField()
    warranty_document = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_display_image(self, obj):
        result = ""
        if obj.display_image:
            split_url = obj.display_image.split('?')
            result = split_url[0]
        return result

    def get_warranty_document(self, obj):
        result = ""
        if obj.warranty_document:
            split_url = obj.warranty_document.split('?')
            result = split_url[0]
        return result


class UpdateInventoryModelSerializer(PermissionSerializerBase):
    def update(self, instance, validated_data):
        if 'quantities' in validated_data:
            nested_data = validated_data.pop('quantities')
            if nested_data:
                for data in self.initial_data['quantities']:
                    existing_quantity = False
                    location_instance = None
                    if 'location' in data:
                        # Adding an amount to a potentially existing material
                        # quantity
                        location_instance = LocationInstance.objects.filter(id=data['location']).first()
                        if not location_instance:
                            # If couldn't get the location, then
                            # location_instance is a Response object
                            raise serializers.ValidationError("Not a valid location")
                    elif 'location' in data:
                        # Setting the amount of an existing material quantity
                        location_instance = data['location']
                        existing_quantity = True
                    self.save_quantities(location_instance, instance, data, existing_quantity)
        return super().update(instance, validated_data)


class TimezoneField(serializers.Field):
    def to_representation(self, obj):
        return six.text_type(obj)

    def to_internal_value(self, data):
        try:
            return pytz.timezone(str(data))
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValidationError('Unknown timezone')
