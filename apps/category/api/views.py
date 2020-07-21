from rest_framework.parsers import JSONParser
from django.shortcuts import get_object_or_404
from apps.category.api.serializers import CategorySerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from apps.category.models import Category
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_list_view(request):
    try:
        category = Category.objects.all()
        serializer = CategorySerializer(category, many=True)
        return Response({
                'status': 'SUCCESS',
                'statusCode': status.HTTP_200_OK,
                'statusMessage': 'categories fetched successfully!',
                'response': serializer.data
            })
    except:
        return Response({
                'status': 'FAILURE',
                'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'statusMessage': 'Some error occurred\n we are working on it...'
            })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_category_view(request):
    try:
        data = JSONParser().parse(request)
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        return Response({
                'status': 'SUCCESS',
                'statusCode': status.HTTP_201_CREATED,
                'statusMessage': 'category added successfully!',
                'response': []
            })
    except:
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'Some error occurred\n we are working on it...'	})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category_view(request, pk):
    try:
        category = get_object_or_404(Category, pk=pk)
        data = JSONParser().parse(request)
        serializer = CategorySerializer(category, data=data)
        if serializer.is_valid():
            serializer.save()
        return Response({
                'status': 'SUCCESS',
                'statusCode': status.HTTP_200_OK,
                'statusMessage': 'category updated successfully!',
                'response': []
            })
    except:
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'Some error occurred\n we are working on it...'	})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_category_view(request, pk):
    try:
        category = get_object_or_404(Category, pk=pk)
        operation = category.delete()
        if operation:
            return Response({
                    'status': 'SUCCESS',
                    'statusCode': status.HTTP_204_NO_CONTENT,
                    'statusMessage': 'category deleted successfully!',
                    'response': []
                })
        return Response({
                'status': 'FAILURE',
                'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'statusMessage': 'Some error occurred\n we are working on it...'	})
    except Exception as e:
        return Response({
            'status': 'FAILURE',
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'statusMessage': 'some internal server error occured'})
