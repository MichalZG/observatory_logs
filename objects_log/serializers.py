from rest_framework import serializers
from objects_log.models import Target
from django.utils import timezone

def auto_end_datetime():
    return timezone.now() + timezone.timedelta(hours=1)

class TargetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    datetime_start = serializers.DateTimeField(default=timezone.now)
    datetime_end = serializers.DateTimeField(default=auto_end_datetime())
    observer = serializers.CharField(default='NB')
    name = serializers.CharField()
    ra = serializers.DecimalField(max_digits=12, decimal_places=10,
        required=False)
    dec = serializers.DecimalField(max_digits=12, decimal_places=10,
        required=False)
    note = serializers.CharField(required=False)
    telescope = serializers.StringRelatedField()
    program = serializers.StringRelatedField()
    colorfilters = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)
    total_exposure_time = serializers.DecimalField(
        max_digits=5, decimal_places=3
    )
    number_of_frames = serializers.ImageField(required=False)


    def create(self, validated_data):
        return Target.objects.create(**validated_data)

    def update(self, validated_data):
        return instance

