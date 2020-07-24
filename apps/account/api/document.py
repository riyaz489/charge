from django_elasticsearch_dsl import Document, Index, fields
from apps.account.models import Account
from django_elasticsearch_dsl.registries import registry


# run this command intially to create or delete old index and create new one for this app in elasticsearch
# `./manage.py search_index --rebuild`

@registry.register_document
class BlogUserDocument(Document):
    class Index:
        name = 'blog_user'
    class Django:
        model = Account
        fields = [
            'email',
            'username',
            'id',
            'image'
        ]