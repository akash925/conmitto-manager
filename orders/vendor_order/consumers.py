from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from djangochannelsrestframework.mixins import ListModelMixin
from django.db.models import QuerySet

from .models import VendorOrder
from api.base.views import get_personnel_org_ids
from api.utils.permissions import IsScopeAuthenticated
from api.serializers import VendorOrderConsumerSerializerBase


class VendorOrderConsumer(ObserverModelInstanceMixin, ListModelMixin, GenericAsyncAPIConsumer):
    model = VendorOrder
    stream = 'vendor_orders'
    serializer_class = VendorOrderConsumerSerializerBase
    permission_classes = (IsScopeAuthenticated, )
    queryset = VendorOrder.objects.all()

    # IMPORTANT get_queryset will cause the subscribe_instance action to fail,
    # this works for filtering based on org_id's for now.
    def filter_queryset(self, queryset: QuerySet, **kwargs):
        """
        Given a queryset, filter it with whichever filter backend is in use.
        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        # TODO filter_backends
        user = self.scope['user']
        org_ids = get_personnel_org_ids(user)

        queryset = queryset.filter(org__in=org_ids).order_by('-created_at')
        return queryset
