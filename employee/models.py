from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

class UserAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def worked_hours(self):
        if self.check_in_time and self.check_out_time:
            total_worked = (self.check_out_time - self.check_in_time).total_seconds() / 3600
            
            # Calculate total break time
            total_break = sum(
                (break_time.break_end_time - break_time.break_start_time).total_seconds() / 3600
                for break_time in self.breaks.all()  # Access related BreakTime instances
                if break_time.break_start_time and break_time.break_end_time
            )
            return total_worked - total_break
        return 0
    
    def __str__(self):
        return f"{self.user.username} - {self.check_in_time} to {self.check_out_time}"
   

class BreakTime(models.Model):
    attendance = models.ForeignKey(UserAttendance, related_name='breaks', on_delete=models.CASCADE)
    break_start_time = models.DateTimeField(null=True, blank=True)
    break_end_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Break from {self.break_start_time} to {self.break_end_time} for {self.attendance.user.username}"
class BreakTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakTime
        fields = ['id', 'attendance', 'break_start_time', 'break_end_time']

class UserAttendanceSerializer(serializers.ModelSerializer):
    breaks = BreakTimeSerializer(many=True, required=False)
    class Meta:
        model = UserAttendance
        fields = ['id', 'user', 'check_in_time', 'check_out_time','breaks'  ,'worked_hours']
    def create(self, validated_data):
        # Extract break data from validated_data
        breaks_data = validated_data.pop('breaks', [])

        # Create the UserAttendance instance
        user_attendance = UserAttendance.objects.create(**validated_data)

        # Create associated BreakTime instances (if any)
        for break_data in breaks_data:
            break_data['attendance'] = user_attendance  # Associate each break with the user_attendance
            BreakTime.objects.create(**break_data)

        return user_attendance
