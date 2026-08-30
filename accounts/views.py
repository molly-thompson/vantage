# Create your views here.
from django.http import HttpRequest, HttpResponse


def dashboard(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Accounts dashboard loads")
