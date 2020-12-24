from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.permissions import IsAuthenticated

from .models import Post, Comment, Follow, Group
from .serializers import PostSerializer, CommentSerializer, FollowSerializer, GroupSerializer
from django.shortcuts import get_object_or_404
from .permissions import IsOwner


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwner]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        group_id = self.request.query_params.get('group', None)
        if group_id is not None:
            group = get_object_or_404(Group, id=group_id)
            queryset = group.posts.all()
        else:
            queryset = Post.objects.all()
        return queryset


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


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
