from rest_framework import serializers
from objects_log.models import Target, ColorFilter, Telescope
from django.utils import timezone
from rest_framework.validators import UniqueTogetherValidator

def auto_end_datetime():
    return timezone.now() + timezone.timedelta(hours=1)


class ColorFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorFilter
        fields = ('name', )

class TelescopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telescope
        fields = ('name', )
        read_only_fields = ('name',)


class TargetSerializer(serializers.ModelSerializer):
    telescope = serializers.SlugRelatedField(
        many=False, read_only=False, queryset=Telescope.objects.all(),
        slug_field='name')
    colorfilters = serializers.SlugRelatedField(
        many=True, read_only=False, queryset=ColorFilter.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = Target
        fields = ['datetime_start', 'datetime_end', 'observer', 'name',
            'ra', 'dec', 'note', 'telescope', 'colorfilters',
            'total_exposure_time', 'number_of_frames',]
        validators = [
            UniqueTogetherValidator(
                queryset=Target.objects.all(),
                fields=['datetime_start', 'telescope',]
            )
        ]

class TargetStatsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        last_datetime = instance.order_by(
            '-datetime_start').first().datetime_start
        counts = instance.count()

        return {
            'last_datetime': last_datetime,
            'counts': counts,
        }
