from rest_framework import serializers
from datetime import date
from apps.account.models import Account, AccountSubscriber
from apps.blog.models import Blog, LikedBy, BlogData
from django.utils import timezone


DUMMY_IMAGE = "https://winatweb.com/wp-content/uploads/2019/04/what-is-a-blog.png"
DUMMY_HEADING = "-------"


class BlogDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogData
        fields = ['type', 'content', 'position']
       # exclude = ['id']


class BlogSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    username = serializers.CharField(source="published_by.username", read_only=True)
    publisher_img = serializers.CharField(source="published_by.image", read_only=True)
    blog_data = BlogDataSerializer(many=True)
    likes = serializers.IntegerField(source="likedby_set.count", min_value=0, read_only=True)

    class Meta:
        model = Blog
        fields = ["id", "is_active", "blog_data", "published_on", "category", "published_by", "category_name",
                  "username", "publisher_img", "likes"]

    def create(self, validated_data):
        validated_data['is_active'] = True
        validated_data['published_on'] = timezone.now()
        temp_data = validated_data.pop('blog_data')
        new_blog = Blog.objects.create(**validated_data)
        for i in temp_data:
            BlogData.objects.create(**i, blog=new_blog)
        return new_blog

    def update(self, instance, validated_data):
        instance.is_active = True
        instance.published_on = timezone.now()
        temp_data = validated_data.pop('blog_data')
        instance.blog_data.all().delete()
        for i in temp_data:
            BlogData.objects.create(**i, blog=instance)
        instance.save()
        return instance


class LikedBySerializer(serializers.ModelSerializer):

    class Meta:
        model = LikedBy
        fields = ["id", "blog", "user"]


class BlogsThumbSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source="likedby_set.count", min_value=0)
    # here we have set source, otherwise its default source will be get_heading
    heading = serializers.SerializerMethodField('is_named_heading')
    image = serializers.SerializerMethodField('is_named_image')
    category_name = serializers.CharField(source='category.name')
    publisher_name = serializers.CharField(source="published_by.username")
    publisher_img = serializers.CharField(source="published_by.image")
    blog_id = serializers.IntegerField(source='id')
    did_i_liked = serializers.SerializerMethodField()
    did_i_follow = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ["blog_id", "published_on", "published_by", "category_name", "publisher_name", "category", "image",
                  "heading", "likes", "did_i_liked", "publisher_img", "did_i_follow"]

    # another way is to  create likes field as SerializerMethodField() and don't set source
    # so its default source name will be get_<field_name>
    # def get_likes(self, obj):
    #     return obj.likedby_set.count

    # here we get single object of blog
    def is_named_heading(self, obj):
        # so now we have single blog object which contains queryobject of blog_data
        temp = obj.blog_data.all().filter(type='HEADING').order_by('position').first()
        result = DUMMY_HEADING
        if temp:
            result = temp.content
        return result

    def is_named_image(self, obj):
        # so now we have single blog object which contains queryobject of blog_data
        temp = obj.blog_data.all().filter(type='IMAGE').order_by('position').first()
        result = DUMMY_IMAGE
        if temp:
            result = temp.content
        return result

    def get_did_i_liked(self, obj):
        # obj = single instance of Blog from Blogs query
        request = self.context.get('request', None)
        current_user = None
        if request:
            current_user = request.user
        if not current_user:
            return False
        temp = LikedBy.objects.filter(blog=obj, user=current_user)
        if temp:
            return True
        return False

    def get_did_i_follow(self, obj):
        # obj = single instance of Blog from Blogs query
        request = self.context.get('request', None)
        current_user = None
        if request:
            current_user = request.user
        if not current_user:
            return False
        temp = AccountSubscriber.objects.filter(current_account=current_user, following_account=obj.published_by)
        if temp:
            return True
        return False


# extending blogsThumbSerializer
class TrendingBlogsSerializer(BlogsThumbSerializer):
    today_likes_count = serializers.IntegerField()

    # for SerializerMethodField()
    # def get_today_likes_count(self, obj):
    #     return obj.likedby_set.filter(liked_on__date=date.today()).count()

    class Meta(BlogsThumbSerializer.Meta):
        fields = BlogsThumbSerializer.Meta.fields + ['today_likes_count', ]
