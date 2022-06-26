from django.contrib import admin

# Register your models here.
from kiosk.models import Category, Menu, Orderinfo, Orderdetail, Shelter

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name');
admin.site.register(Category, CategoryAdmin);

class MenuAdmin(admin.ModelAdmin):
    list_display = ('id','name','price','category_id', 'image');
admin.site.register(Menu,MenuAdmin);

class OrderdetailAdmin(admin.ModelAdmin):
    list_display = ('id','orderinfo_id','menu_id', 'amount');
admin.site.register(Orderdetail, OrderdetailAdmin);

class OrderinfoAdmin(admin.ModelAdmin):
    list_display = ('id','weather','process_time','order_time','senior', 'gender', 'shelter_id');
admin.site.register(Orderinfo, OrderinfoAdmin);

class ShelterAdmin(admin.ModelAdmin):
    list_display = ('id','name','latitude','longitude');
admin.site.register(Shelter, ShelterAdmin);