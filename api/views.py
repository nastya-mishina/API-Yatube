from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.permissions import IsAuthenticated

from .models import Post, Comment, Follow, Group
from .serializers import PostSerializer, CommentSerializer, FollowSerializer, GroupSerializer
from django.shortcuts import get_object_or_404
from .permissions import IsOwner


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwner]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['group']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwner]

    def perform_create(self, serializer):
        get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        serializer.save(author=self.request.user)

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        return post.comments


class FollowViewSet(viewsets.ModelViewSet, mixins.CreateModelMixin,
                    mixins.ListModelMixin):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ['user__username']
    filtered_fields = ['following']

    def perform_create(self, serializer):
        if serializer.is_valid:
            serializer.save(user=self.request.user)
        else:
            serializer.errors

    def get_queryset(self):
        return self.request.user.following.all()


class GroupViewSet(viewsets.ModelViewSet, mixins.CreateModelMixin,
                   mixins.ListModelMixin):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
