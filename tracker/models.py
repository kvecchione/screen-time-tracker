"""
Models for the Screen Time Tracker application.
"""
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class Child(models.Model):
    """Model representing a child to track screen time for."""
    name = models.CharField(max_length=100)
    baseline_weekly_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Weekly baseline screen time allocated each Monday"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "children"
    
    def __str__(self):
        return self.name
    
    def get_weekly_reset_date(self):
        """Get the Monday of the current week for this child."""
        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())
        return monday


class ScreenTimeGoal(models.Model):
    """Model representing a daily screen time goal for children."""
    GOAL_TYPES = [
        ('binary', 'Binary (Earned/Not Earned)'),
        ('tracked', 'Tracked (Hours/Minutes)'),
    ]
    
    DAYS_OF_WEEK = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]
    
    children = models.ManyToManyField(
        Child,
        related_name='goals',
        help_text="Children this goal applies to",
        db_table='tracker_goal_children'
    )
    name = models.CharField(max_length=200, help_text="Goal name (e.g., 'Math Practice', 'Reading')")
    goal_type = models.CharField(
        max_length=20,
        choices=GOAL_TYPES,
        default='binary',
        help_text="Type of goal: binary (done/not done) or tracked (time-based)"
    )
    reward_minutes = models.PositiveIntegerField(help_text="Screen time reward in minutes for completing this goal")
    reward_per_hour = models.PositiveIntegerField(
        default=0,
        help_text="Reward minutes per hour for tracked goals (e.g., 30 minutes screen time per hour of reading)"
    )
    bonus_minutes = models.PositiveIntegerField(
        default=5,
        help_text="Additional bonus minutes for completing without being asked"
    )
    target_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Target minutes for tracked goals (e.g., 120 for 2 hours of reading)"
    )
    applies_to_days = models.CharField(
        max_length=50,
        default='mon,tue,wed,thu,fri,sat,sun',
        help_text="Comma-separated days (mon,tue,wed,thu,fri,sat,sun)"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display for goals")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        child_names = ', '.join([c.name for c in self.children.all()])
        return f"{self.name} ({child_names})" if child_names else self.name
    
    def applies_today(self):
        """Check if this goal applies today."""
        today = timezone.now().date()
        day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        today_code = day_map[today.weekday()]
        days_list = [d.strip() for d in self.applies_to_days.split(',')]
        return today_code in days_list


class DailyTracking(models.Model):
    """Model for daily goal tracking."""
    STATUS_CHOICES = [
        ('earned', 'Earned'),
        ('not_earned', 'Not Earned'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='daily_trackings', help_text="Child this tracking belongs to")
    goal = models.ForeignKey(ScreenTimeGoal, on_delete=models.CASCADE, related_name='daily_trackings')
    date = models.DateField(help_text="Date of the tracking")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_earned')
    minutes_earned = models.PositiveIntegerField(default=0, help_text="Minutes of screen time earned")
    actual_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Actual minutes spent on tracked goals (e.g., 90 minutes of reading)"
    )
    bonus_earned = models.BooleanField(default=False, help_text="Whether the bonus was earned (done without being asked)")
    notes = models.TextField(blank=True, help_text="Notes about the day's performance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', 'goal']
        unique_together = ['child', 'goal', 'date']
        indexes = [
            models.Index(fields=['child', 'date', 'goal']),
            models.Index(fields=['goal', 'date']),
        ]
    
    def __str__(self):
        return f"{self.child.name} - {self.goal} - {self.date} ({self.status})"


class AdhocReward(models.Model):
    """Model for manually awarded ad-hoc rewards to a child."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='adhoc_rewards')
    minutes = models.PositiveIntegerField(help_text="Minutes rewarded")
    reason = models.CharField(max_length=200, help_text="Reason for the reward")
    awarded_date = models.DateField(auto_now_add=True, help_text="Date the reward was given")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-awarded_date', '-created_at']
        indexes = [
            models.Index(fields=['child', 'awarded_date']),
        ]
    
    def __str__(self):
        return f"{self.child.name} - {self.minutes} mins ({self.reason})"


class AdhocPenalty(models.Model):
    """Model for manually applied ad-hoc penalties to a child."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='adhoc_penalties')
    minutes = models.PositiveIntegerField(help_text="Minutes penalized")
    reason = models.CharField(max_length=200, help_text="Reason for the penalty")
    applied_date = models.DateField(auto_now_add=True, help_text="Date the penalty was applied")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_date', '-created_at']
        indexes = [
            models.Index(fields=['child', 'applied_date']),
        ]
        verbose_name_plural = "penalties"
    
    def __str__(self):
        return f"{self.child.name} - {self.minutes} mins penalty ({self.reason})"

