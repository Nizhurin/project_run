from rest_framework import viewsets
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
    queryset = Run.objects.all()
    serializer_class = RunSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().exclude(is_superuser=True)
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = self.queryset  # Используем базовый queryset определенный выше, на уровне класса
        user_type = self.request.query_params.get('type', None)  # Получим параметр type
        is_stuff = False
        if user_type:
            if user_type == 'coach':
                is_stuff = True
            qs = qs.filter(is_staff=is_stuff)
        return qs
