from rest_framework.viewsets import ModelViewSet
from .models import Blog
from .serializer.BlogSerializer import BlogSerializer


class BlogViewSet(ModelViewSet):
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()

