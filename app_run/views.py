from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

from app_run.models import Run, User
from app_run.serializers import RunSerializer, UserSerializer


@api_view(['GET'])
def company_details(request):
    details = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS
    }
    return Response(details)

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().exclude(is_superuser=True)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter] # Подключаем SearchFilter здесь
    search_fields = ['first_name', 'last_name'] # Указываем поля по которым будет вестись поиск

    def get_queryset(self):
        qs = self.queryset  # Используем базовый queryset определенный выше, на уровне класса
        user_type = self.request.query_params.get('type', None)  # Получим параметр type
        is_stuff = False
        if user_type:
            if user_type == 'coach':
                is_stuff = True
            qs = qs.filter(is_staff=is_stuff)
        return qs

class RunStartAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == 'init':
            run.status = 'in_progress'
            run.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class RunStopAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == 'in_progress':
            run.status = 'finished'
            run.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
