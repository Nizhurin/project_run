from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem


class AthleteDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']

class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteDataSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()  # Задаем вычисляемое поле type
    runs_finished = serializers.IntegerField(read_only=True)  # Задаем вычисляемое поле runs_finished

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = AthleteInfo
        fields = ("user_id", "goals", "weight")

    def validate_weight(self, value):
        if value <= 0 or value >= 900:
            raise serializers.ValidationError(
                "weight must be > 0 and < 900"
            )
        return value

class ChallengeSerializer(serializers.ModelSerializer):
    athlete = serializers.IntegerField(source="athlete_id", read_only=True)

    class Meta:
        model = Challenge
        fields = ("athlete", "full_name")

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ("id", "run", "latitude", "longitude")
        read_only_fields = ("id",)

    def validate_latitude(self, latitude):
        if latitude < -90 or latitude > 90:
            raise serializers.ValidationError(
                "Latitude must be in range [-90.0, 90.0]."
            )
        return latitude

    def validate_longitude(self, longitude):
        if longitude < -180 or longitude > 180:
            raise serializers.ValidationError(
                "Longitude must be in range [-180.0, 180.0]."
            )
        return longitude

    def validate_run(self, run):
        if run.status != 'in_progress':
            raise serializers.ValidationError(
                 "Run must be in status 'in_progress'."
            )
        return run

class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = '__all__'
