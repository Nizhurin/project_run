from django.conf import settings
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Run, User, AthleteInfo
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer


@api_view(['GET'])
def company_details(request):
    details = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS
    }
    return Response(details)

class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'  # Разрешаем изменять количество объектов через query параметр size в url

class UserPagination(PageNumberPagination):
    page_size_query_param = 'size'  # Разрешаем изменять количество объектов через query параметр size в url

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter] # Указываем какй класс будет использоваться для фильтра
    filterset_fields = ['status', 'athlete'] # Поля, по которым будет происходить фильтрация
    ordering_fields = ['created_at']  # Поля по которым будет возможна сортировка
    pagination_class = RunPagination  # Указываем пагинацию


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().exclude(is_superuser=True)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name'] # Указываем поля по которым будет вестись поиск
    ordering_fields = ['date_joined']  # Поля по которым будет возможна сортировка
    pagination_class = UserPagination  # Указываем пагинацию

    def get_queryset(self):
        qs = self.queryset  # Используем базовый queryset определенный выше, на уровне класса
        user_type = self.request.query_params.get('type', None)  # Получим параметр type
        is_stuff = False
        if user_type:
            if user_type == 'coach':
                is_stuff = True
            qs = qs.filter(is_staff=is_stuff)
        #  подсчет finished-run для каждого пользователя
        qs = qs.annotate(
            runs_finished=Count('run', filter=Q(run__status='finished'))
        )
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

class AthleteAPIView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        athlete_info, _ = AthleteInfo.objects.get_or_create(user_id=user)

        serializer = AthleteInfoSerializer(athlete_info)
        return Response(serializer.data)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        athlete_info, _ = AthleteInfo.objects.get_or_create(user_id=user)

        serializer = AthleteInfoSerializer(
            athlete_info,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
