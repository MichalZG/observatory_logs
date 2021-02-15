from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

from objects_log.models import Target
from objects_log.serializers import TargetSerializer, TargetStatsSerializer


@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated,))
def target_list(request):

    if request.method == 'GET':
        targets = Target.objects.all()
        serializer = TargetSerializer(targets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        print(request.data)
        serializer = TargetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
def target_stats(request):

    if request.method == 'GET':
        targets = Target.objects.all()
        serializer = TargetStatsSerializer(targets)
        return Response(serializer.data)