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
        # Allow client to request summary for a specific date via `date` query param
        date_param = request.query_params.get('date')
        if date_param:
            try:
                today = datetime.strptime(date_param, '%Y-%m-%d').date()
            except Exception:
                today = timezone.now().date()
        else:
            today = timezone.now().date()
        
        # Collect goals that apply for this day
        day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        day_code = day_map[today.weekday()]

        all_goals = ScreenTimeGoal.objects.filter(child=child, is_active=True).order_by('order')
        applicable_goals = [g for g in all_goals if day_code in [d.strip() for d in (g.applies_to_days or '').split(',')]]

        # Fetch existing trackings for applicable goals on this date
        trackings_qs = DailyTracking.objects.filter(goal__in=applicable_goals, date=today).select_related('goal')

        # Build a mapping goal_id -> tracking
        tracking_map = {t.goal_id: t for t in trackings_qs}

        # Prepare goals list: include a synthetic tracking for goals without one
        goals_list = []
        earned = 0
        not_earned = 0
        total_target = 0
        total_earned = 0

        for g in applicable_goals:
            total_target += g.target_minutes or 0
            t = tracking_map.get(g.id)
            if t:
                goals_list.append(t)
                total_earned += t.minutes_earned or 0
                if t.status == 'earned':
                    earned += 1
                elif t.status == 'not_earned':
                    not_earned += 1
            else:
                # synthetic 'not_earned' tracking (default)
                not_earned += 1
                goals_list.append(DailyTracking(goal=g, date=today, status='not_earned', minutes_earned=0, actual_minutes=0, bonus_earned=False))

        summary = {
            'date': today,
            'child_id': child.id,
            'child_name': child.name,
            'total_target_minutes': total_target,
            'total_earned_minutes': total_earned,
            'pending_goals': 0,
            'earned_goals': earned,
            'not_earned_goals': not_earned,
            'goals': DailyTrackingSerializer(goals_list, many=True).data
        }
        
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def weekly_summary(self, request, pk=None):
        """Get current week's tracking summary for a child."""
        child = self.get_object()
        # Allow client to request the week containing a specific date via `date` query param
        date_param = request.query_params.get('date')
        if date_param:
            try:
                ref_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except Exception:
                ref_date = timezone.now().date()
        else:
            ref_date = timezone.now().date()

        monday = ref_date - timedelta(days=ref_date.weekday())
        sunday = monday + timedelta(days=6)
        
        # Get all trackings for the week
        trackings = DailyTracking.objects.filter(
            goal__child=child,
            date__gte=monday,
            date__lte=sunday
        ).select_related('goal')

        # Only count minutes for trackings where the goal applies to that tracking's weekday
        day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        total_earned = 0
        for t in trackings:
            day_code = day_map[t.date.weekday()]
            applies = day_code in [d.strip() for d in (t.goal.applies_to_days or '').split(',')]
            if applies and t.status == 'earned':
                total_earned += t.minutes_earned or 0

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

    @action(detail=False, methods=['post'])
    def batch(self, request):
        """Return trackings for multiple goals and/or dates in one request.

        Expects JSON body with optional keys:
          - goal_ids: [int, int, ...]
          - dates: ["YYYY-MM-DD", ...]

        Returns serialized DailyTracking objects that match any of the provided
        goal_ids and dates.
        """
        goal_ids = request.data.get('goal_ids') or []
        dates = request.data.get('dates') or []

        qs = DailyTracking.objects.all().select_related('goal')
        if goal_ids:
            qs = qs.filter(goal_id__in=goal_ids)
        if dates:
            qs = qs.filter(date__in=dates)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


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
