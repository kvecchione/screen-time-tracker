"""
Serializers for the Screen Time Tracker API.
"""
from rest_framework import serializers
from .models import Child, ScreenTimeGoal, DailyTracking, AdhocReward


class ScreenTimeGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenTimeGoal
        fields = [
            'id', 'name', 'goal_type', 'reward_minutes', 'reward_per_hour', 'bonus_minutes',
            'target_minutes', 'applies_to_days', 'is_active', 'order'
        ]
        read_only_fields = ['id']


class DailyTrackingSerializer(serializers.ModelSerializer):
    goal_name = serializers.CharField(source='goal.name', read_only=True)
    
    class Meta:
        model = DailyTracking
        fields = [
            'id', 'goal', 'goal_name', 'date', 'status', 
            'minutes_earned', 'actual_minutes', 'bonus_earned', 'notes'
        ]
        read_only_fields = ['id']


class ChildDetailSerializer(serializers.ModelSerializer):
    goals = ScreenTimeGoalSerializer(many=True, read_only=True)
    
    class Meta:
        model = Child
        fields = ['id', 'name', 'baseline_weekly_minutes', 'goals', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChildListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'name', 'baseline_weekly_minutes']
        read_only_fields = ['id']


class DailyTrackingSummarySerializer(serializers.Serializer):
    """Serializer for daily tracking summary across all goals for a child."""
    date = serializers.DateField()
    child_id = serializers.IntegerField()
    child_name = serializers.CharField()
    total_target_minutes = serializers.IntegerField()
    total_earned_minutes = serializers.IntegerField()
    pending_goals = serializers.IntegerField()
    earned_goals = serializers.IntegerField()
    not_earned_goals = serializers.IntegerField()
    goals = DailyTrackingSerializer(many=True)


class AdhocRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdhocReward
        fields = [
            'id', 'child', 'minutes', 'reason', 'awarded_date', 'created_at'
        ]
        read_only_fields = ['id', 'awarded_date', 'created_at']
