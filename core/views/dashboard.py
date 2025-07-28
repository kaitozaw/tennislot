from core.models import BookingPage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard_view(request):
    booking_pages = BookingPage.objects.filter(organiser=request.user)

    return render(request, "dashboard/index.html", {
        "booking_pages": booking_pages
    })