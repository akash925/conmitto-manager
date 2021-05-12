from rest_framework import serializers

from api.orders.materials.serializers import MaterialOrderSerializer
from api.orders.vendor_order.models import VendorOrderType, VendorOrder, VendorOrderMaterialInstance, \
    VendorOrderIssue, VendorOrderIssueComment, VendorOrderNote
from api.personnel.serializers import PersonnelNameSerializer, BaseOrgModelSerializer


class VendorOrderNameSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = VendorOrder
        fields = ('id', 'org', 'status', 'date', 'title')

    def get_status(self, obj):
        return obj.get_status_display()


class VendorOrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorOrderType
        exclude = ['org']


class VendorOrderMaterialInstanceSerializer(serializers.ModelSerializer):
    material = MaterialOrderSerializer()

    class Meta:
        model = VendorOrderMaterialInstance
        fields = '__all__'


class VendorOrderIssueCommentSerializer(serializers.ModelSerializer):
    author = PersonnelNameSerializer(read_only=True)

    class Meta:
        model = VendorOrderIssueComment
        fields = '__all__'


class VendorOrderIssueSerializer(serializers.ModelSerializer):
    issue_comments = VendorOrderIssueCommentSerializer(many=True, required=False)

    class Meta:
        model = VendorOrderIssue
        fields = '__all__'


class UpdateVendorOrderSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(required=False, queryset=VendorOrderType.objects.all(), allow_null=True)
    date = serializers.DateField(format="%Y-%m-%d", required=False, allow_null=True)
    materials = VendorOrderMaterialInstanceSerializer(many=True, required=False, read_only=True)
    issues = VendorOrderIssueSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = VendorOrder
        exclude = ['org']


class NewVendorOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorOrder
        exclude = ['type', 'status']


class VendorOrderNoteSerializer(BaseOrgModelSerializer):
    class Meta:
        model = VendorOrderNote
        exclude = ['vendor_order']
