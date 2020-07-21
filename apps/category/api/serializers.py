from rest_framework import serializers
from apps.category.models import Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['name', 'id']
    extra_kwargs = {
        'id': {'write_only': True, 'read_only': True},
    }


