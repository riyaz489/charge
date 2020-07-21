from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from apps.account.api.serializers import RegistrationSerializer, UserLoginSerializer, BlogsListSerilizer,\
	UserProfleSerializer
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.shortcuts import get_object_or_404
from apps.account.models import Account, AccountSubscriber
from apps.account.api.document import BlogUserDocument
from elasticsearch_dsl.query import Q


FOLLOW = 'FOLLOW'
UN_FOLLOW = 'UN_FOLLOW'

@api_view(['POST', ])
@permission_classes([AllowAny, ])
def registration_view(request):

	try:
		if request.method == 'POST':
			serializer = RegistrationSerializer(data=request.data)
			data = {}
			if serializer.is_valid():
				account, token = serializer.save()
				data['statusMessage'] = 'successfully registered new user.'
				data['status'] = 'SUCCESS'
				data['statusCode'] = '201'
				data['response'] = {'token': token}
				return Response(data, status=status.HTTP_201_CREATED)
			else:
				res = {}
				data = serializer.errors
				if len(data.keys()) > 1:
					temp = 'email and username is not unique'
				else:
					temp = list(data.values())[0][0]
				res['statusCode'] = '400'
				res["status"] = "FAILURE"
				res["statusMessage"] = temp
				return Response(res, status=status.HTTP_200_OK)
	except Exception as e:
		return Response({
			'status': 'FAILURE',
			'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
			'statusMessage': 'some internal server error occured'})


@api_view(['POST', ])
@permission_classes([AllowAny, ])
def login_view(request):
	try:
		serializer = UserLoginSerializer(data=request.data)
		response = {}
		if serializer.is_valid():
			response = {
				'status': 'SUCCESS',
				'statusCode': '200',
				'statusMessage': 'User logged in  successfully',
				'response': {'token':  serializer.data['token'], 'username': serializer.data['username']}
				}
		else:
			temp = ''
			if 'non_field_errors' in serializer.errors:
				temp = serializer.errors['non_field_errors'][0]

			else:
				for key, value in serializer.errors.items():
					for v in value:
						temp += str(key)+': '+ str(v)+', '
			response = {'status': 'FAILURE', 'statusCode': status.HTTP_400_BAD_REQUEST, 'statusMessage': temp}
		return Response(response, status=status.HTTP_200_OK)
	except Exception as e:
		return Response({
			'status': 'FAILURE',
			'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
			'statusMessage': 'some internal server error occured'})


@api_view(['PUT', ])
@permission_classes([IsAuthenticated, ])
def add_profile_image(request):
	try:
		user_profile = request.user
		data = JSONParser().parse(request)
		if 'url' not in data:
			raise Http404("url needed in request body")
		req = {'image': data['url']}
		serializer = UserProfleSerializer(user_profile, data=req, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({
				'status': 'SUCCESS',
				'statusCode': status.HTTP_200_OK,
				'statusMessage': 'image uploaded successfully!',
				'response': serializer.data})
		temp = ''
		for key, value in serializer.errors.items():
			for v in value:
				temp += str(key) + ': ' + str(v) + ', '
		return Response({'status': 'FAILURE', 'statusCode': status.HTTP_400_BAD_REQUEST, 'statusMessage': temp})

	except Exception as e:
		return Response({
			'status': 'FAILURE',
			'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
			'statusMessage': 'some internal server error occured'})



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def change_subscribe_relation_status(request):
	try:
		data = JSONParser().parse(request)
		current_user = request.user
		# check if key in dict
		if not data.keys() >= {"status", "username"}:
			raise Http404('relationship status is required')
		# raise exception if not found
		following_account = Account.objects.get(username=data['username'])
		success_status_message = ''
		if data['status'] == FOLLOW:
			# add
			AccountSubscriber.objects.get_or_create(current_account=current_user,   following_account=following_account)
			success_status_message = 'Account followed successfully !'
		elif data['status'] == UN_FOLLOW:
			#remove
			AccountSubscriber.objects.filter(current_account=current_user, following_account=following_account).delete()
			success_status_message = 'Account un-followed successfully !'
		else:
			return Response({
			'status': 'FAILURE',
			'statusCode': status.HTTP_400_BAD_REQUEST,
			'statusMessage': 'status is incorrect, set `FOLLOW` or `UN_FOLLOW`'})

		return Response({
			'status': 'SUCCESS',
			'statusCode': status.HTTP_204_NO_CONTENT,
			'statusMessage': success_status_message})
	except Exception as e:
		return Response({
			'status': 'FAILURE',
			'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
			'statusMessage': 'some internal server error occured'})


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def check_follow_status(request, pk):
	try:
		current_user = request.user
		following_user = get_object_or_404(Account, pk=pk)
		following_status = AccountSubscriber.objects.filter(current_account=current_user, following_account=following_user)
		is_followed = False
		if following_status:
			is_followed = True
		return Response(
			{
				'status': 'SUCCESS',
				'statusCode': status.HTTP_200_OK,
				'statusMessage': 'account status fetched successfully!',
				'response': {
					'user_id': following_user.id,
					'is_followed': is_followed,
					'user_image': following_user.image
				}
			}
		)
	except Exception as e:
		return Response({
			'status': 'FAILURE',
			'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
			'statusMessage': 'some internal server error occured'})


class UserProfileView(RetrieveAPIView):

	permission_classes = (IsAuthenticated,)
	authentication_class = JSONWebTokenAuthentication

	# fetch current user all blogs
	def get(self, request):

		try:
			user_profile = request.user
			result = BlogsListSerilizer(user_profile, context={'request': request})
			response = {
				'status': 'SUCCESS',
				'statusCode': status.HTTP_200_OK,
				'statusMessage': 'blog fetched successfully!',
				'response': result.data
			}
			return Response(response)
		except Exception as e:
			return Response({
				'status': 'FAILURE',
				'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
				'statusMessage': 'some internal server error occured'})

	# fetch child data using parent object with the help of <relation_name>__<col_name>
		# data = Blog.objects.filter(published_by=user_profile.id).filter(blog_data__type='HEADING').values()

		# below command will return list of child table data (result of child table query) inside each
		# attribute we defined here
		#     data = Blog.objects.prefetch_related(Prefetch(
		#     'blog_data',
		#         # we always need queryset here so can't use first and last function in query here
		#     queryset=BlogData.objects.filter(type="IMAGE").order_by('position'),
		#     to_attr='img'
		# )).prefetch_related(Prefetch(
		#     'blog_data',
		#     queryset=BlogData.objects.filter(type="HEADING").order_by('position'),
		#     to_attr='hd'
		# ))
		#     for product in data:
		#         print(product.id)
		#         for latest_revision in product.img:
		#             print(product.id, latest_revision.type, latest_revision.position)
		#     return Response(data.values())

		# temp = Blog.objects.filter(published_by=user_profile.id).first()
		# result = temp.blog_data.all().filter(type='HEADING').order_by('position')


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def search(request):
	try:
		q = request.GET.get('q')
		current_user = request.user
		data = []
		if q:
			data = []
			user = BlogUserDocument.search().query(Q("prefix", username=q)|Q("prefix", email=q))
			for u in user:
				following_user = Account.objects.get(pk=u.id)
				temp = AccountSubscriber.objects.filter(current_account=current_user, following_account=following_user)
				is_following = False
				if temp:
					is_following = True
				data.append({'image': u.image, 'username': u.username, 'is_following': is_following, 'email': u.email})
		return Response({
			'status': 'SUCCESS',
			'statusCode': status.HTTP_200_OK,
			'statusMessage': 'users fetched successfully!',
			'response': data
		})
	except Exception as e:
		return Response({
			'status': 'FAILURE',
			'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
			'statusMessage': 'some internal server error occured'})





