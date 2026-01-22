"""
Tests for the tracker app.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import Child, ScreenTimeGoal, DailyTracking


class ChildModelTests(TestCase):
    def setUp(self):
        self.child = Child.objects.create(name='Emma')
    
    def test_child_creation(self):
        self.assertEqual(self.child.name, 'Emma')
    
    def test_get_weekly_reset_date(self):
        monday = self.child.get_weekly_reset_date()
        self.assertEqual(monday.weekday(), 0)  # Monday is 0


class ScreenTimeGoalTests(TestCase):
    def setUp(self):
        self.child = Child.objects.create(name='Emma')
        self.goal = ScreenTimeGoal.objects.create(
            child=self.child,
            name='Math Practice',
            target_minutes=30,
            baseline_weekly_minutes=150
        )
    
    def test_goal_creation(self):
        self.assertEqual(self.goal.name, 'Math Practice')
        self.assertEqual(self.goal.target_minutes, 30)
        self.assertTrue(self.goal.is_active)


class DailyTrackingTests(TestCase):
    def setUp(self):
        self.child = Child.objects.create(name='Emma')
        self.goal = ScreenTimeGoal.objects.create(
            child=self.child,
            name='Math Practice',
            target_minutes=30,
            baseline_weekly_minutes=150
        )
        self.today = timezone.now().date()
    
    def test_tracking_creation(self):
        tracking = DailyTracking.objects.create(
            goal=self.goal,
            date=self.today,
            status='earned',
            minutes_earned=30
        )
        self.assertEqual(tracking.status, 'earned')
        self.assertEqual(tracking.minutes_earned, 30)
    
    def test_unique_goal_date(self):
        DailyTracking.objects.create(
            goal=self.goal,
            date=self.today,
            status='earned',
            minutes_earned=30
        )
        
        # Should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            DailyTracking.objects.create(
                goal=self.goal,
                date=self.today,
                status='earned',
                minutes_earned=30
            )


class APIAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_children_list_requires_auth(self):
        response = self.client.get('/api/children/')
        self.assertEqual(response.status_code, 401)
