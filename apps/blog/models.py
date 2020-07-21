from django.core.validators import MinValueValidator
from django.db import models
from apps.category.models import Category
from apps.account.models import Account

BLOG_DATA_TYPES = (("HEADING", "HEADING"), ("SUBHEADING", "SUBHEADING"), ("IMAGE", "IMAGE"), ("PARAGRAPH", "PARAGRAPH"))


class Blog(models.Model):
    is_active = models.BooleanField(default=True)
    published_on = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    published_by = models.ForeignKey(Account, on_delete=models.CASCADE)


class LikedBy(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    liked_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('blog', 'user'),)


class BlogData(models.Model):
    type = models.CharField(
        max_length=30,
        choices=BLOG_DATA_TYPES
    )
    content = models.TextField()
    position = models.IntegerField(null=False, validators=[MinValueValidator(0)])
    # relation_name is used to fetch data frm reverse side i.e Blog table in our case
    # (default name of realtions is model_set, i.e blogdata_set in our case)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="blog_data")

    class Meta:
        unique_together = (('blog', 'position'),)