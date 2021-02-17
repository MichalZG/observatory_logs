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
        extra_kwargs = {
            'name': {'validators': []},
        }

class TelescopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telescope
        fields = ('name', )
        # read_only_fields = ('name',)
        extra_kwargs = {
            'name': {'validators': []},
        }

class TargetSerializer(serializers.ModelSerializer):
    telescope = serializers.SlugRelatedField(
        many=False, read_only=False, queryset=Telescope.objects.all(),
        slug_field='name')
    # colorfilters = serializers.SlugRelatedField(
    #     many=True, read_only=False, queryset=ColorFilter.objects.all(),
    #     slug_field='name'
    # )
    # telescope = TelescopeSerializer(many=False)
    colorfilters = ColorFilterSerializer(many=True)

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

    def create(self, validated_data):
        colorfilters_data = validated_data.pop('colorfilters')
        # telescope_data = validated_data.pop('telescope') 

        target = Target.objects.create(**validated_data)
        if colorfilters_data:
            for c_filter_data in colorfilters_data:
                c_filter, _ = ColorFilter.objects.get_or_create(
                    **c_filter_data
                )
                target.colorfilters.add(c_filter)

        return target

class TargetStatsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        last_datetime = instance.order_by(
            '-datetime_start').first().datetime_start
        counts = instance.count()

        return {
            'last_datetime': last_datetime,
            'counts': counts,
        }
