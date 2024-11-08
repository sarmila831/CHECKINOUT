from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import UserAttendance,UserAttendanceSerializer

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from django.utils import timezone
from . import views
'''class Home(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)'''
class UserAttendanceViewSet(viewsets.ModelViewSet):
    queryset = UserAttendance.objects.all()
    serializer_class = UserAttendanceSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        attendance = self.get_object()
        if attendance.check_in_time and not attendance.check_out_time:
            attendance.check_out_time = timezone.now()
            attendance.save()
            serializer = self.get_serializer(attendance)
            return Response(serializer.data)
        return Response({"detail": "Cannot check out without checking in."}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if user_id:
            self.queryset = self.queryset.filter(user_id=user_id)
        return super().list(request, *args, **kwargs)
