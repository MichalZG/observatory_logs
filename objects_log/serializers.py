from rest_framework import serializers
from objects_log.models import Observer, Target, ColorFilter, Telescope
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


class ObserverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observer
        fields = ('name', )
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
    observers = ObserverSerializer(many=True)

    class Meta:
        model = Target
        fields = ['datetime_start', 'datetime_end', 'observers', 'name',
            'ra', 'dec', 'note', 'telescope', 'colorfilters',
            'total_exposure_time', 'number_of_frames',]
        validators = [
            UniqueTogetherValidator(
                queryset=Target.objects.all(),
                fields=['datetime_start', 'telescope',]
            )
        ]

    
    def add_colorfilters(self, target, data):
        if data:
            for c_filter_data in data:
                c_filter, _ = ColorFilter.objects.get_or_create(
                    **c_filter_data
                )
                target.colorfilters.add(c_filter)
            return True
        return False

    def add_observers(self, target, data):
        if data:
            for o_data in data:
                observer, _ = Observer.objects.get_or_create(
                    **o_data
                )
                target.observers.add(observer)
            return True
        return False

    def create(self, validated_data):
        # telescope_data = validated_data.pop('telescope') 
        colorfilters_data = validated_data.pop('colorfilters')
        observers_data = validated_data.pop('observers')

        target = Target.objects.create(**validated_data)

        self.add_colorfilters(target, colorfilters_data)
        self.add_observers(target, observers_data)

        return target


class TargetStatsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        last_instance = instance.order_by(
            '-datetime_start').first()

        if not last_instance:
            last_datetime = None
        else:
            last_datetime = last_instance.datetime_start
            
        counts = instance.count()

        return {
            'last_datetime': last_datetime,
            'counts': counts,
        }
