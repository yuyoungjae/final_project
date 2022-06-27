from django.shortcuts import render
from django.views import View
from django.db import connection
from django_request_mapping import request_mapping

from kiosk.models import Menu

import os
from .rdsmysql import *

@request_mapping("")
class MyView(View):
    orderlist = list()
    
    def __init__(self):
        MyView.imgs = dict()
        MyView.imgs2 = dict()
        
        with connection.cursor() as cursor:
            # 이미지
            for menu in select_table(cursor, "KIOSK", "menu"):
                name = menu[1]
                id = menu[0]
                file_path = f"static/img/food/{id:02d}_{name}.jpg"

                # if os.path.isfile(file_path.lstrip("/")) == False:
                #     print(file_path, "없음")
                    
                #     img = Image.open(BytesIO(base64.b64decode(menu[4])))
                #     img.save(file_path)
                MyView.imgs2[id] = str(menu[4], 'utf-8')
                # MyView.imgs2[id] = base64.b64decode()
                
                # MyView.imgs[id] = "/"+file_path
    
    @request_mapping("/", method="get")
    def index_init(self, request):
        return self.index(request)
    
    
    # path("", views.cocktails),
    @request_mapping("<int:id>/", method="get")
    def index(self, request, id=7):
        context = dict()


        context['category_id'] = id if 1 <= id <= 7 else 7
            
        if context["category_id"] == 6:
            with connection.cursor() as cursor:
            
                objs = list()
                
                for obj in get_top_menu(cursor, top_cnt=5):
                    recommand_id = obj[0]
                    objs.append(Menu.objects.filter(id=recommand_id).values("id", "name", "price", "category_id")[0])

        else:
            objs = Menu.objects.values("id", "name", "price", "category_id")
            
        context['objs'] = objs
        
        
        for idx, obj in enumerate(objs):
            # objs[idx]["file_path"] = MyView.imgs[obj["id"]]
            objs[idx]["img"] = MyView.imgs2[obj["id"]]
        
        print(objs[0]["img"][:10])
            
        return render(request, 'index.html', context)
                                                                    
    @request_mapping("senior/", method="get")
    def index_init2(self, request):
        return self.index2(request)
    
    
    # path("", views.cocktails),
    @request_mapping("senior/<int:id>/", method="get")
    def index2(self, request, id=7):
        context = dict()


        context['category_id'] = id if 1 <= id <= 7 else 7
            
        if context["category_id"] == 6:
            with connection.cursor() as cursor:
            
                objs = list()
                
                for obj in get_top_menu(cursor, top_cnt=5):
                    recommand_id = obj[0]
                    objs.append(Menu.objects.filter(id=recommand_id).values("id", "name", "price", "category_id")[0])

        else:
            objs = Menu.objects.values("id", "name", "price", "category_id")
            
        context['objs'] = objs
        
        
        for idx, obj in enumerate(objs):
            objs[idx]["img"] = MyView.imgs2[obj["id"]]
        
        return render(request, 'index2.html', context)
                                                                    