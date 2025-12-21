from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Run, AthleteInfo


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
