from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, LoginSerializer, UserProfileSerializer,
    UserListSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'first_name', 'last_name', 'date_joined']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions required for this view.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]  # Allow registration
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()

        # Admins can see all users
        if user.role == 'admin' or user.is_staff:
            return User.objects.all()

        # Coaches can see their team players
        if user.role == 'coach':
            return User.objects.filter(
                Q(teams__coach=user) | Q(id=user.id)
            ).distinct()

        # Regular users can only see themselves
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def me(self, request):
        """Get current user profile"""
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.AllowAny])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def change_password(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Removed stray indentation error
    def by_role(self, request):
        """Get users filtered by role"""
        role = request.query_params.get('role')
        if not role:
            return Response({'error': 'Role parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(role=role)
        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)


class LoginView(APIView):
    """
    API view for user login
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
                    permission_classes = [permissions.AllowAny]
                    return [permission() for permission in permission_classes]
class LogoutView(APIView):
    """
    API view for user logout
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class RegisterView(APIView):
    """
    API view for user registration
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Registration successful',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CoachViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for coaches - read-only access
    """
    queryset = User.objects.filter(role='coach', is_active=True)
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'username']
    ordering = ['first_name', 'last_name']


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for players - read-only access
    """
    queryset = User.objects.filter(role__in=['player', 'child'], is_active=True)
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role']
    search_fields = ['first_name', 'last_name', 'username']
    ordering = ['first_name', 'last_name']

    def get_queryset(self):
        """
        Filter players based on user permissions
        """
        user = self.request.user
        if user.role == 'admin' or user.is_staff:
            return self.queryset
        elif user.role == 'coach':
            # Coaches can see their team players
            return User.objects.filter(
                role__in=['player', 'child'],
                is_active=True,
                teams__coach=user
            ).distinct()
        return User.objects.none()
