from django.urls import path
from apps.blog.api.views import get_blog, publish_blog, get_following_blogs, set_likes, get_trending_blogs, \
   remove_blog, update_blog

app_name = 'blog'

urlpatterns = [
   path('fetch/<int:pk>', get_blog, name="fetch blog"),
   path('add', publish_blog, name="add blog"),
   path('remove/<int:pk>', remove_blog, name="remove blog"),
   path('update/<int:pk>', update_blog, name="update blog"),
   path('followings', get_following_blogs, name="following blogs"),
   path('trending', get_trending_blogs, name="trending blogs"),
   path('like', set_likes, name="set likes")
]