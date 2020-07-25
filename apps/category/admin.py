from django.contrib.auth.admin import UserAdmin
from apps.category.models import Category
from django.contrib import admin


class CategoryAdmin(admin.ModelAdmin):
	fields = ['name', 'id']
	readonly_fields = ['id', ]


admin.site.register(Category, CategoryAdmin)