from django.shortcuts import render
from django.views import View
from django.db import connection
from django_request_mapping import request_mapping

from kiosk.models import Menu

from .rdsmysql import *

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


        context['category_id'] = id if 1 <= id <= 7 else 7
            
        if context["category_id"] == 6:
            with connection.cursor() as cursor:
            
                objs = list()
                
                for obj in get_top_menu(cursor, top_cnt=5):
                    recommand_id = obj[0]
                    objs.append(Menu.objects.filter(id=recommand_id).values("name", "price", "category_id")[0])

        else:
            objs = Menu.objects.values("name", "price", "category_id")
            
        context['objs'] = objs
        # print(objs)
            
        return render(request, 'index.html', context)
