from django.shortcuts import render
from django.views import View
from django_request_mapping import request_mapping

from kiosk.models import Menu


@request_mapping("")
class MyView(View):
    orderlist = list()
    
    # def __init__(self):
        # orderlist = list()
    
    @request_mapping("/", method="get")
    def index_init(self, request):
        return self.index(request)
    
    
    # path("", views.cocktails),
    @request_mapping("<int:id>/", method="get")
    def index(self, request, id=6):
        context = dict()

        objs = Menu.objects.values("name", "price", "category_id")

        context['objs'] = objs
        context['category_id'] = id if 1 <=id <=5 else 6
            
            
        return render(request, 'index.html', context)
