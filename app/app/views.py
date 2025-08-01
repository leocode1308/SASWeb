from django.http import HttpResponse
from django.shortcuts import render
from visits.models import PageVisits
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
#import request

LOGIN_URL = settings.LOGIN_URL


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

VALID_CODE = "abc1234"

def pw_protected_view(request, *args, **kwargs):
    is_allowed = request.session.get('protected_page_allowed') or 0
    print("Hola")
    print(request.session.items())
    print(f"Valor de 'protected_page_allowed' en sesión: {is_allowed}") # Debugging line
    print(request.session.get('protected_page_allowed'), type(request.session.get('protected_page_allowed')))
    if request.method == "POST":
        user_pw_sent = request.POST.get("code") or None
        if user_pw_sent == VALID_CODE:
            is_allowed = 1
            request.session['protected_page_allowed'] = is_allowed
            print("Hola 2")
            print(f"Valor de 'protected_page_allowed' en sesión: {is_allowed}") # Debugging line
    if is_allowed:
        return render(request, "protected/view.html", {})
    return render(request, "protected/entry.html", {})

@login_required(login_url=LOGIN_URL)
def user_only_view(request, *args, **kwargs):
    # print(request.user.is_staff)
    return render(request, "protected/user-only.html", {})

@staff_member_required(login_url=LOGIN_URL)
def staff_only_view(request, *args, **kwargs):
    # print(request.user.is_staff)
    return render(request, "protected/user-only.html", {})