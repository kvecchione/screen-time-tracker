"""
Admin interface for the Screen Time Tracker.
"""
from django.contrib import admin
from .models import Child, ScreenTimeGoal, DailyTracking, AdhocReward


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'baseline_weekly_minutes', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'baseline_weekly_minutes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ScreenTimeGoal)
class ScreenTimeGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_children', 'goal_type', 'reward_minutes', 'reward_per_hour', 'bonus_minutes', 'target_minutes', 'applies_to_days', 'is_active']
    list_filter = ['is_active', 'goal_type', 'created_at']
    search_fields = ['name', 'children__name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['children']
    
    def get_children(self, obj):
        return ', '.join([c.name for c in obj.children.all()])
    get_children.short_description = 'Children'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('children', 'name', 'goal_type', 'is_active')
        }),
        ('Binary Goal Settings', {
            'fields': ('reward_minutes', 'bonus_minutes', 'applies_to_days'),
            'description': 'Used for binary (earned/not earned) goals'
        }),
        ('Tracked Goal Settings', {
            'fields': ('target_minutes', 'reward_per_hour'),
            'description': 'Used for tracked (hours/minutes) goals'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DailyTracking)
class DailyTrackingAdmin(admin.ModelAdmin):
    list_display = ['child', 'goal', 'date', 'status', 'minutes_earned', 'actual_minutes', 'bonus_earned']
    list_filter = ['status', 'bonus_earned', 'date', 'child', 'created_at']
    search_fields = ['goal__name', 'goal__children__name', 'child__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Goal & Date', {
            'fields': ('child', 'goal', 'date')
        }),
        ('Performance', {
            'fields': ('status', 'minutes_earned', 'actual_minutes', 'bonus_earned', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AdhocReward)
class AdhocRewardAdmin(admin.ModelAdmin):
    list_display = ['child', 'minutes', 'reason', 'awarded_date']
    list_filter = ['awarded_date', 'child', 'created_at']
    search_fields = ['reason', 'child__name']
    readonly_fields = ['awarded_date', 'created_at', 'updated_at']
    date_hierarchy = 'awarded_date'
    
    fieldsets = (
        ('Child & Reward', {
            'fields': ('child', 'minutes', 'reason')
        }),
        ('Metadata', {
            'fields': ('awarded_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
