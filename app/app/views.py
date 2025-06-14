from django.http import HttpResponse
from django.shortcuts import render
from visits.models import PageVisits
#import request


def home_view(request, *args, **kwargs):
    return about_view(request, *args, **kwargs)

def about_view(request, *args, **kwargs):
    """
    Render the home page.
    """
    qs = PageVisits.objects.all()
    page_qs = PageVisits.objects.filter(path=request.path)
    my_context = {
        "page_visits_count": page_qs.count(),
        "total_visits_count": qs.count(),
        "percent": (page_qs.count() / qs.count()) * 100 if qs.count() > 0 else 0,
    }
    path = request.path
    #print("qs:", qs, type(qs))
    PageVisits.objects.create(path=request.path)
    html_template = "app/index.html"
    return render(request, html_template, my_context)