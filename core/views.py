# Create your views here.
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from global_login_required import login_not_required


@login_not_required  # type: ignore[untyped-decorator]
def home(request: HttpRequest) -> HttpResponse:
    return render(request, "core/home.html")
