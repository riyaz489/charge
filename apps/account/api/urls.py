from django.urls import path
from django.conf.urls import url
from apps.account.api.views import(
	registration_view,
	login_view,
	UserProfileView,
	add_profile_image,
	change_subscribe_relation_status,
	check_follow_status,
	search
)


app_name = 'account'

urlpatterns = [
	path('register', registration_view, name="register"),
	path('login', login_view, name="login"),
	path('profile/add_img', add_profile_image, name="add profile image"),
	url(r'^profile', UserProfileView.as_view()),
	path('relation', change_subscribe_relation_status, name='change relation status'),
	path('follow/status/<int:pk>', check_follow_status, name='follow status'),
	path('search', search, name='search')

]