from django_request_mapping import UrlPattern
from kiosk.views import MyView

urlpatterns = UrlPattern()
urlpatterns.register(MyView)
