from django.urls import path
from django.conf.urls import url
from apps.category.api.views import category_list_view, add_category_view, update_category_view, delete_category_view

app_name = 'category'

urlpatterns = [
   path('list', category_list_view, name="category_list"),
   path('add', add_category_view, name="add_category"),
   path('update/<int:pk>', update_category_view, name="update_category"),
   path('del/<int:pk>', delete_category_view, name="delete_category")

]