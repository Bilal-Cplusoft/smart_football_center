from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Session, Booking, Bundle, Membership, Discount
from .serializers import (
    SessionSerializer, SessionCreateSerializer, SessionListSerializer,
    BookingSerializer, BookingCreateSerializer, BundleSerializer,
    MembershipSerializer, DiscountSerializer, ApplyDiscountSerializer,
    SessionStatsSerializer
)
from smart_football_center.accounts.models import User


class SessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sessions
    """
    queryset = Session.objects.all().select_related('coach')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['session_type', 'coach']
    search_fields = ['name', 'coach__first_name', 'coach__last_name']
    ordering_fields = ['date', 'name', 'price']
    ordering = ['date']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return SessionCreateSerializer
        elif self.action == 'list':
            return SessionListSerializer
        return SessionSerializer

    def get_queryset(self):
        """Filter sessions based on query parameters"""
        queryset = self.queryset

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        # Filter upcoming sessions
        if self.request.query_params.get('upcoming') == 'true':
            queryset = queryset.filter(date__gte=timezone.now())

        # Filter available sessions (not full)
        if self.request.query_params.get('available') == 'true':
            queryset = queryset.filter(spots_left__gt=0)

        return queryset

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming sessions"""
        sessions = self.get_queryset().filter(
            date__gte=timezone.now()
        ).order_by('date')[:10]

        serializer = SessionListSerializer(sessions, many=True)
        return Response({
            'upcoming_sessions': serializer.data
        })

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available sessions (not full)"""
        sessions = self.get_queryset().filter(
            spots_left__gt=0,
            date__gte=timezone.now()
        ).order_by('date')

        serializer = SessionListSerializer(sessions, many=True)
        return Response({
            'available_sessions': serializer.data
        })

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Get all bookings for this session"""
        session = self.get_object()
        bookings = Booking.objects.filter(session=session).select_related('player')

        serializer = BookingSerializer(bookings, many=True)
        return Response({
            'session': session.name,
            'bookings_count': bookings.count(),
            'bookings': serializer.data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get session statistics"""
        now = timezone.now()

        total_sessions = Session.objects.count()
        upcoming_sessions = Session.objects.filter(date__gte=now).count()
        past_sessions = total_sessions - upcoming_sessions
        full_sessions = Session.objects.filter(spots_left=0).count()
        total_bookings = Booking.objects.count()

        # Calculate revenue from bookings
        revenue = Session.objects.aggregate(
            total=Sum('price')
        )['total'] or 0

        stats_data = {
            'total_sessions': total_sessions,
            'upcoming_sessions': upcoming_sessions,
            'past_sessions': past_sessions,
            'full_sessions': full_sessions,
            'total_bookings': total_bookings,
            'revenue': revenue
        }

        serializer = SessionStatsSerializer(data=stats_data)
        serializer.is_valid()
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings
    """
    queryset = Booking.objects.all().select_related('player', 'session')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'session__session_type']
    search_fields = ['player__first_name', 'player__last_name', 'session__name']
    ordering_fields = ['booked_at', 'session__date']
    ordering = ['-booked_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        """Filter bookings based on user permissions"""
        user = self.request.user
        queryset = self.queryset

        # Admins can see all bookings
        if user.role == 'admin' or user.is_staff:
            return queryset

        # Coaches can see bookings for their sessions
        if user.role == 'coach':
            return queryset.filter(session__coach=user)

        # Players can see their own bookings
        if user.role in ['player', 'child']:
            return queryset.filter(player=user)

        return Booking.objects.none()

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get current user's bookings"""
        user = request.user
        bookings = Booking.objects.filter(player=user).select_related('session')

        serializer = BookingSerializer(bookings, many=True)
        return Response({
            'bookings_count': bookings.count(),
            'bookings': serializer.data
        })

    @action(detail=False, methods=['post'])
    def book_session(self, request):
        """Book a session for the current user"""
        data = request.data.copy()
        data['player'] = request.user.id

        serializer = BookingCreateSerializer(data=data)
        if serializer.is_valid():
            booking = serializer.save()
            return Response(
                BookingSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Cancel booking and restore session spots"""
        booking = self.get_object()
        session = booking.session

        # Restore spot to session
        session.spots_left += 1
        session.save()

        # Delete booking
        self.perform_destroy(booking)

        return Response({
            'message': f'Booking cancelled for {session.name}'
        })


class BundleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bundles
    """
    queryset = Bundle.objects.all().select_related('owner')
    serializer_class = BundleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['owner']
    ordering = ['-id']

    def get_queryset(self):
        """Filter bundles based on user permissions"""
        user = self.request.user

        # Admins can see all bundles
        if user.role == 'admin' or user.is_staff:
            return self.queryset

        # Users can see their own bundles
        return self.queryset.filter(owner=user)

    @action(detail=False, methods=['get'])
    def my_bundles(self, request):
        """Get current user's bundles"""
        user = request.user
        bundles = Bundle.objects.filter(owner=user)

        serializer = BundleSerializer(bundles, many=True)
        return Response({
            'bundles_count': bundles.count(),
            'bundles': serializer.data
        })

    @action(detail=True, methods=['post'])
    def use_credit(self, request, pk=None):
        """Use a credit from the bundle"""
        bundle = self.get_object()

        if bundle.credits_left() <= 0:
            return Response(
                {'error': 'No credits remaining in this bundle'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if bundle.expiry_date < timezone.now().date():
            return Response(
                {'error': 'Bundle has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bundle.sessions_used += 1
        bundle.save()

        return Response({
            'message': 'Credit used successfully',
            'credits_remaining': bundle.credits_left()
        })


class MembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing memberships
    """
    queryset = Membership.objects.all().select_related('owner')
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['active', 'plan_name']
    ordering = ['-start_date']

    def get_queryset(self):
        """Filter memberships based on user permissions"""
        user = self.request.user

        # Admins can see all memberships
        if user.role == 'admin' or user.is_staff:
            return self.queryset

        # Users can see their own memberships
        return self.queryset.filter(owner=user)

    @action(detail=False, methods=['get'])
    def my_membership(self, request):
        """Get current user's active membership"""
        user = request.user
        membership = Membership.objects.filter(owner=user, active=True).first()

        if membership:
            serializer = MembershipSerializer(membership)
            return Response(serializer.data)
        else:
            return Response({
                'message': 'No active membership found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        """Freeze membership"""
        membership = self.get_object()

        if membership.freeze_count >= 3:  # Maximum 3 freezes per membership
            return Response(
                {'error': 'Maximum freeze limit reached'},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.active = False
        membership.freeze_count += 1
        membership.save()

        return Response({
            'message': 'Membership frozen successfully',
            'freeze_count': membership.freeze_count
        })

    @action(detail=True, methods=['post'])
    def unfreeze(self, request, pk=None):
        """Unfreeze membership"""
        membership = self.get_object()

        membership.active = True
        membership.save()

        return Response({
            'message': 'Membership unfrozen successfully'
        })


class DiscountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing discounts
    """
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['active']
    search_fields = ['code', 'description']
    ordering = ['-id']

    def get_permissions(self):
        """No authentication required for any action"""
        permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def apply(self, request):
        """Apply discount code to calculate final amount"""
        serializer = ApplyDiscountSerializer(data=request.data)

        if serializer.is_valid():
            return Response({
                'original_amount': serializer.validated_data['total_amount'],
                'discount_code': serializer.validated_data['discount_object'].code,
                'discount_percentage': serializer.validated_data['discount_object'].percentage,
                'discount_amount': serializer.validated_data['discount_amount'],
                'final_amount': serializer.validated_data['final_amount']
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active discounts"""
        discounts = Discount.objects.filter(active=True)
        serializer = DiscountSerializer(discounts, many=True)

        return Response({
            'active_discounts': serializer.data
        })
