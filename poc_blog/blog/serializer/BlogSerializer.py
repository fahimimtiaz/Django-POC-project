from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from ..models import Blog


class BlogSerializer(ModelSerializer):

    class Meta:
        model = Blog
        fields = '__all__'
