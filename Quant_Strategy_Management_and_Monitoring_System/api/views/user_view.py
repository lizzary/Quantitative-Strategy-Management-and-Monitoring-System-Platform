from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, serializers


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = User
                fields = ['id', 'username', 'email']

        return Serializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)