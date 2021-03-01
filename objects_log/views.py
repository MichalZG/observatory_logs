from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination

from objects_log.models import Target, Telescope
from objects_log.serializers import TargetSerializer, TargetStatsSerializer

from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger('django')

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    max_page_size = 100

@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated,))
def target_list(request):

    if request.method == 'GET':
        paginator = StandardResultsSetPagination()
        targets = Target.objects.all()
        result_page = paginator.paginate_queryset(targets, request)
        serializer = TargetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        serializer = TargetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"{request.data}\n {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((permissions.IsAuthenticated,))
def target_detail(request, pk):
    try:
        target = Target.objects.get(pk=pk)
    except Target.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TargetSerializer(target)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TargetSerializer(target, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def targets_stats(request):

    if request.method == 'GET':
        targets = Target.objects.all()
        serializer = TargetStatsSerializer(targets)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def targets_stats_telescope(request, tname):

    if request.method == 'GET':
        try:
            telescope = Telescope.objects.get(name=tname)
        except ObjectDoesNotExist:
            return Response(f'The {tname} telescope was not found in the DB',
                status=status.HTTP_400_BAD_REQUEST)
        targets = Target.objects.filter(telescope=telescope)
        serializer = TargetStatsSerializer(targets)
        return Response(serializer.data)