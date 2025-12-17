from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import serializers
from .models import Run


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
    runs_finished = serializers.SerializerMethodField()  # Задаем вычисляемое поле runs_finished

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        return User.objects.annotate(finished_runs_count=Count('run', filter=Q(run__status='finished')))
