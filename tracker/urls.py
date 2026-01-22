"""
URL routing for the tracker app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChildViewSet, ScreenTimeGoalViewSet, 
    DailyTrackingViewSet, AdhocRewardViewSet
)

router = DefaultRouter()
router.register(r'children', ChildViewSet, basename='child')
router.register(r'goals', ScreenTimeGoalViewSet, basename='goal')
router.register(r'daily-tracking', DailyTrackingViewSet, basename='daily-tracking')
router.register(r'adhoc-rewards', AdhocRewardViewSet, basename='adhoc-reward')

urlpatterns = [
    path('', include(router.urls)),
]
