from datetime import date
from django.db.models import Prefetch, Q, Count, Case, When
from django.http import Http404
from rest_framework.fields import IntegerField
from rest_framework.parsers import JSONParser
from django.shortcuts import get_object_or_404
from apps.account.models import AccountSubscriber
from apps.blog.api.serializers import BlogSerializer, BlogsThumbSerializer, TrendingBlogsSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from apps.blog.models import Blog, LikedBy, BlogData
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_blog(request):

    try:
        user_profile = request.user
        data = JSONParser().parse(request)
        data['published_by'] = user_profile.id
        serializer = BlogSerializer(data=data)
        if serializer.is_valid():
            # save will call create or update method
            serializer.save()
            response = {
                'status': 'SUCCESS',
                'statusCode': status.HTTP_200_OK,
                'statusMessage': 'blog published successfully!',
                'response': []
            }
            return Response(response)
        else:
            return Response({
                'status': 'FAILURE',
                'statusCode': status.HTTP_400_BAD_REQUEST,
                'statusMessage': str(serializer.errors)
            })
    except Exception as e:
        print(e)
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'some internal server error occured'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_blog(request, pk):

    try:
        data = get_object_or_404(Blog, pk=pk)
        serializer = BlogSerializer(data)
        temp = serializer.data
        response = {
            'status': 'SUCCESS',
            'statusCode': status.HTTP_200_OK,
            'statusMessage': 'blog fetched successfully!',
            'response': temp
        }
        return Response(response)
    except Exception as e:
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'some internal server error occured'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_following_blogs(request):
    try:
        user_profile = request.user
        followings_list = AccountSubscriber.objects.filter(current_account=user_profile.id)
        followings_ids_list =[]
        for followings in followings_list:
            followings_ids_list.append(followings.following_account.id)
        following_blogs = Blog.objects.\
            filter(Q(published_by__id__in=followings_ids_list)| Q(published_by=user_profile.id)).order_by('published_on')
        result = BlogsThumbSerializer(following_blogs, many=True, context={
            'request': request
        })
        response = {
            'status': 'SUCCESS',
            'statusCode': status.HTTP_200_OK,
            'statusMessage': 'blogs fetched successfully!',
            'response': result.data
        }
        return Response(response)
    except Exception as e:
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'some internal server error occured'})


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def set_likes(request):
    try:
        data = JSONParser().parse(request)
        current_user = request.user
        # check if key in dict
        if not data.keys() >= {"status", "blog_id"}:
            raise Http404('relationship status is required')
        current_blog = Blog.objects.get(pk=data['blog_id'])
        success_status_message = ''
        if data['status']:
            # add
            LikedBy.objects.get_or_create(user=current_user,   blog=current_blog)
            success_status_message = 'Like added successfully !'
        elif not data['status']:
            #remove
            LikedBy.objects.filter(user=current_user, blog=current_blog).delete()
            success_status_message = 'Like removed successfully !'
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trending_blogs(request):
    try:
        blogs_with_today_likes_count = Blog.objects.annotate(
            today_likes_count=Count(
                Case(
                    When(likedby__liked_on__date=date.today(), then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('-today_likes_count', 'published_on')

        result = TrendingBlogsSerializer(blogs_with_today_likes_count, many=True, context={
            'request': request
        })
        response = {
            'status': 'SUCCESS',
            'statusCode': status.HTTP_200_OK,
            'statusMessage': 'blogs fetched successfully!',
            'response': result.data
        }
        return Response(response)
    except Exception as e:
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'some internal server error occured'})


@api_view(['DELETE', ])
@permission_classes([IsAuthenticated, ])
def remove_blog(request, pk):
    try:
        current_user = request.user
        blog_data = Blog.objects.filter(pk=pk, published_by=current_user)
        success_status_message = ''
        if blog_data:
            blog_data.delete()
            success_status_message = 'Blog removed successfully !'
        else:
            success_status_message = "Blog not found!"

        return Response({
            'status': 'SUCCESS',
            'statusCode': status.HTTP_204_NO_CONTENT,
            'statusMessage': success_status_message})
    except Exception as e:
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'some internal server error occured'})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_blog(request, pk):

    try:
        user_profile = request.user
        old_blog_data = Blog.objects.get(pk=pk, published_by=user_profile)
        if not old_blog_data:
            return Response({
                'status': 'FAILURE',
                'statusCode': status.HTTP_400_BAD_REQUEST,
                'statusMessage': 'Blog not found!'
            })
        data = JSONParser().parse(request)
        serializer = BlogSerializer(old_blog_data, data=data, partial=True)
        if serializer.is_valid():
            # save will call create or update method
            serializer.save()
            response = {
                'status': 'SUCCESS',
                'statusCode': status.HTTP_200_OK,
                'statusMessage': 'blog published successfully!',
                'response': []
            }
            return Response(response)
        else:
            return Response({
                'status': 'FAILURE',
                'statusCode': status.HTTP_400_BAD_REQUEST,
                'statusMessage': str(serializer.errors)
            })
    except Exception as e:
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'some internal server error occured'})

