# from django_elasticsearch_dsl import Document, Index, fields
# from apps.account.models import Account
# from django_elasticsearch_dsl.registries import registry
#
#
# @registry.register_document
# class BlogUserDocument(Document):
#     class Index:
#         name = 'blog_user'
#     class Django:
#         model = Account
#         fields = [
#             'email',
#             'username',
#             'id',
#             'image'
#         ]