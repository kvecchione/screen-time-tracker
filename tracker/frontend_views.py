"""
Views for serving the mobile frontend.
"""
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def index(request):
    """Serve the mobile app frontend."""
    return render(request, 'index.html')
