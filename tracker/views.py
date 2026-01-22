"""
Views for the Screen Time Tracker API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import datetime, timedelta

from .models import Child, ScreenTimeGoal, DailyTracking, AdhocReward
from .serializers import (
    ChildDetailSerializer, ChildListSerializer, ScreenTimeGoalSerializer,
    DailyTrackingSerializer, AdhocRewardSerializer,
    DailyTrackingSummarySerializer
)


class ChildViewSet(viewsets.ModelViewSet):
    """ViewSet for managing children."""
    queryset = Child.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChildDetailSerializer
        return ChildListSerializer
    
    @action(detail=True, methods=['get'])
    def daily_summary(self, request, pk=None):
        """Get today's tracking summary for a child."""
        child = self.get_object()
        today = timezone.now().date()
        
        trackings = DailyTracking.objects.filter(goal__child=child, date=today)
        
        total_target = trackings.aggregate(
            total=Sum('goal__target_minutes')
        )['total'] or 0
        total_earned = trackings.aggregate(
            total=Sum('minutes_earned')
        )['total'] or 0
        
        status_counts = trackings.values('status').annotate(count=Sum(1))
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        summary = {
            'date': today,
            'child_id': child.id,
            'child_name': child.name,
            'total_target_minutes': total_target,
            'total_earned_minutes': total_earned,
            'pending_goals': status_dict.get('pending', 0),
            'earned_goals': status_dict.get('earned', 0),
            'not_earned_goals': status_dict.get('not_earned', 0),
            'goals': DailyTrackingSerializer(trackings, many=True).data
        }
        
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def weekly_summary(self, request, pk=None):
        """Get current week's tracking summary for a child."""
        child = self.get_object()
        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        
        # Get all trackings for the week
        trackings = DailyTracking.objects.filter(
            goal__child=child,
            date__gte=monday,
            date__lte=sunday
        )
        
        # Calculate totals
        total_earned = trackings.filter(
            status='earned'
        ).aggregate(
            total=Sum('minutes_earned')
        )['total'] or 0
        
        summary = {
            'child_id': child.id,
            'child_name': child.name,
            'week_start': monday,
            'week_end': sunday,
            'total_baseline_minutes': child.baseline_weekly_minutes,
            'total_earned_minutes': total_earned,
            'total_available_minutes': child.baseline_weekly_minutes + total_earned,
        }
        
        return Response(summary)


class ScreenTimeGoalViewSet(viewsets.ModelViewSet):
    """ViewSet for managing screen time goals."""
    queryset = ScreenTimeGoal.objects.all()
    serializer_class = ScreenTimeGoalSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        child_id = self.request.query_params.get('child_id')
        if child_id:
            return ScreenTimeGoal.objects.filter(child_id=child_id).order_by('order')
        return ScreenTimeGoal.objects.all().order_by('order')
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder goals by updating their order field."""
        goals_order = request.data.get('goals', [])
        updated_goals = []
        
        for idx, goal_id in enumerate(goals_order):
            try:
                goal = ScreenTimeGoal.objects.get(id=goal_id)
                goal.order = idx
                goal.save()
                updated_goals.append(ScreenTimeGoalSerializer(goal).data)
            except ScreenTimeGoal.DoesNotExist:
                pass
        
        return Response({'updated': updated_goals})
    
    def perform_create(self, serializer):
        child_id = self.request.data.get('child_id')
        child = Child.objects.get(id=child_id)
        
        goal = serializer.save(child=child)


class DailyTrackingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing daily tracking."""
    queryset = DailyTracking.objects.all()
    serializer_class = DailyTrackingSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        goal_id = self.request.query_params.get('goal_id')
        date = self.request.query_params.get('date')
        
        queryset = DailyTracking.objects.all()
        
        if goal_id:
            queryset = queryset.filter(goal_id=goal_id)
        if date:
            queryset = queryset.filter(date=date)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update multiple daily trackings."""
        trackings_data = request.data.get('trackings', [])
        updated = []
        
        for tracking_data in trackings_data:
            tracking_id = tracking_data.get('id')
            try:
                tracking = DailyTracking.objects.get(id=tracking_id)
                serializer = self.get_serializer(
                    tracking, data=tracking_data, partial=True
                )
                if serializer.is_valid():
                    tracking = serializer.save()
                    self._update_weekly_allocation(tracking)
                    updated.append(serializer.data)
            except DailyTracking.DoesNotExist:
                pass
        
        return Response({'updated': updated})


class AdhocRewardViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ad-hoc rewards."""
    queryset = AdhocReward.objects.all()
    serializer_class = AdhocRewardSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        child_id = self.request.query_params.get('child_id')
        if child_id:
            return AdhocReward.objects.filter(child_id=child_id)
        return AdhocReward.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()
