from dry_rest_permissions.generics import DRYPermissions
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from rest_flex_fields import FlexFieldsModelViewSet
from rest_framework import filters, status
from rest_framework.response import Response

from .filters import InOrgFilterBackend, NestedViewFilter, InOrgNestedFilterBackend, build_lookup_expresion
from .decorators import DefaultPaginator
from ..logging import LoggingMixin


class BaseViewSet(FlexFieldsModelViewSet):
    permission_classes = [IsAuthenticated]
    org_filter = InOrgFilterBackend
    filter_backends = [org_filter, filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]


class BasePaginatedViewSet(FlexFieldsModelViewSet):
    """
    ViewSet with only a DefaultPaginator and no permission or filters
    """
    pagination_class = DefaultPaginator


class PaginatedViewSet(BaseViewSet):
    """
    Paginated ViewSet that inherits from BaseViewSet
    Has InOrgFilterBackend plus search and ordering filters.
    """
    pagination_class = DefaultPaginator


class BaseNestedOrgViewSet(FlexFieldsModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [InOrgNestedFilterBackend, filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]


class NestedOrgPaginatedViewSet(BaseNestedOrgViewSet):
    pagination_class = DefaultPaginator


class NestedViewSet(FlexFieldsModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [NestedViewFilter, filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]

    def perform_create(self, serializer):
        nested_exp = build_lookup_expresion(self)
        serializer.save(
            **nested_exp
        )


class NestedViewSetCreatedBy(NestedViewSet):
    def perform_create(self, serializer):
        nested_exp = build_lookup_expresion(self)
        serializer.save(
            created_by=self.request.user.personnel,
            **nested_exp
        )


class NoteView(LoggingMixin, NestedViewSetCreatedBy):
    permission_classes = [IsAuthenticated, DRYPermissions]
    ordering = ['-created_at']

    def __init__(self, *args, **kwargs):
        self.nested_value = '{}s_pk'.format(self.nested_field)
        self.filterset_fields = [self.nested_field]
        super().__init__(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.content = request.data['content']
        if 'status' in request.data:
            instance.status = request.data['status']
        setattr(instance, "asset_id", self.kwargs[self.nested_value])
        instance.save()
        return Response(status=status.HTTP_200_OK)


class ColorTypeView(LoggingMixin, NestedViewSet):
    permission_classes = [IsAuthenticated, DRYPermissions]
    nested_field = 'org'
    nested_value = 'orgs_pk'

    def destroy_no_default(self):
        """
        Deletes the object, only if it is not a default object.
        Meant to overload the destroy function

        :return rest_framework.response.Response: The response to return to the user
        """
        instance = self.get_object()
        if instance.is_default:
            return Response(status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
