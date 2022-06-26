from django.shortcuts import render
from django.views import View
from django_request_mapping import request_mapping


@request_mapping("")
class MyView(View):

    @request_mapping("/", method="get")
    def index(self, request):
        from kiosk.models import Menu
        objs = Menu.objects.all()

        context = {
            'objs': objs
        }
        return render(request, 'index.html', context)