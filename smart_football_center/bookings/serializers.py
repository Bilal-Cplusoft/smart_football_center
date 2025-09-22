from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from .models import Session, Booking, Bundle, Membership, Discount
from smart_football_center.accounts.serializers import UserListSerializer


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for Session model with all details"""
    coach_name = serializers.SerializerMethodField()
    spots_available = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    bookings_count = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 'name', 'session_type', 'coach', 'coach_name',
            'date', 'duration_minutes', 'price', 'capacity',
            'spots_left', 'spots_available', 'is_full', 'bookings_count'
        ]
        read_only_fields = ['id', 'spots_left']

    def get_coach_name(self, obj):
        """Get coach's full name"""
        if obj.coach:
            return f"{obj.coach.first_name} {obj.coach.last_name}".strip()
        return "No Coach Assigned"

    def get_spots_available(self, obj):
        """Calculate available spots"""
        return obj.spots_left

    def get_is_full(self, obj):
        """Check if session is full"""
        return obj.spots_left <= 0

    def get_bookings_count(self, obj):
        """Get number of bookings for this session"""
        return obj.booking_set.count()


class SessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sessions"""
    coach_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Session
        fields = [
            'name', 'session_type', 'coach_id', 'date',
            'duration_minutes', 'price', 'capacity'
        ]

    def validate_date(self, value):
        """Validate session date is not in the past"""
        if value < timezone.now():
            raise serializers.ValidationError("Session date cannot be in the past.")
        return value

    def validate_duration_minutes(self, value):
        """Validate duration is reasonable"""
        if value < 15 or value > 480:  # 15 minutes to 8 hours
            raise serializers.ValidationError("Duration must be between 15 minutes and 8 hours.")
        return value

    def validate_price(self, value):
        """Validate price is not negative"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_capacity(self, value):
        """Validate capacity is reasonable"""
        if value < 1 or value > 100:
            raise serializers.ValidationError("Capacity must be between 1 and 100.")
        return value

    def validate_coach_id(self, value):
        """Validate coach exists and has correct role"""
        if value:
            from smart_football_center.accounts.models import User
            try:
                coach = User.objects.get(id=value)
                if coach.role != 'coach':
                    raise serializers.ValidationError("Selected user is not a coach.")
                if not coach.is_active:
                    raise serializers.ValidationError("Coach account is inactive.")
            except User.DoesNotExist:
                raise serializers.ValidationError("Coach not found.")
        return value

    def create(self, validated_data):
        """Create session with coach assignment"""
        coach_id = validated_data.pop('coach_id', None)

        # Set spots_left equal to capacity initially
        validated_data['spots_left'] = validated_data['capacity']

        session = Session.objects.create(**validated_data)

        if coach_id:
            from smart_football_center.accounts.models import User
            coach = User.objects.get(id=coach_id)
            session.coach = coach
            session.save()

        return session


class SessionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for session lists"""
    coach_name = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 'name', 'session_type', 'coach_name',
            'date', 'formatted_date', 'duration_minutes',
            'price', 'capacity', 'spots_left', 'is_full'
        ]

    def get_coach_name(self, obj):
        """Get coach's full name"""
        if obj.coach:
            return f"{obj.coach.first_name} {obj.coach.last_name}".strip()
        return "No Coach"

    def get_is_full(self, obj):
        """Check if session is full"""
        return obj.spots_left <= 0

    def get_formatted_date(self, obj):
        """Get formatted date string"""
        return obj.date.strftime("%Y-%m-%d %H:%M")


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    player_name = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()
    session_date = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'player', 'player_name', 'session',
            'session_name', 'session_date', 'booked_at', 'status'
        ]
        read_only_fields = ['id', 'booked_at']

    def get_player_name(self, obj):
        """Get player's full name"""
        return f"{obj.player.first_name} {obj.player.last_name}".strip()

    def get_session_name(self, obj):
        """Get session name"""
        return obj.session.name

    def get_session_date(self, obj):
        """Get session date"""
        return obj.session.date


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings"""

    class Meta:
        model = Booking
        fields = ['player', 'session']

    def validate(self, attrs):
        """Validate booking creation"""
        player = attrs['player']
        session = attrs['session']

        # Check if session has available spots
        if session.spots_left <= 0:
            raise serializers.ValidationError("Session is fully booked.")

        # Check if player already booked this session
        if Booking.objects.filter(player=player, session=session).exists():
            raise serializers.ValidationError("Player has already booked this session.")

        # Check if session is in the future
        if session.date < timezone.now():
            raise serializers.ValidationError("Cannot book past sessions.")

        return attrs

    def create(self, validated_data):
        """Create booking and update session spots"""
        booking = Booking.objects.create(**validated_data)

        # Decrease available spots
        session = booking.session
        session.spots_left = max(0, session.spots_left - 1)
        session.save()

        return booking


class BundleSerializer(serializers.ModelSerializer):
    """Serializer for Bundle model"""
    owner_name = serializers.SerializerMethodField()
    credits_remaining = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Bundle
        fields = [
            'id', 'owner', 'owner_name', 'sessions_included',
            'sessions_used', 'credits_remaining', 'expiry_date', 'is_expired'
        ]
        read_only_fields = ['id']

    def get_owner_name(self, obj):
        """Get owner's full name"""
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip()

    def get_credits_remaining(self, obj):
        """Get remaining credits"""
        return obj.credits_left()

    def get_is_expired(self, obj):
        """Check if bundle is expired"""
        return obj.expiry_date < timezone.now().date()


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for Membership model"""
    owner_name = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    days_until_renewal = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = [
            'id', 'owner', 'owner_name', 'start_date', 'active',
            'plan_name', 'renewal_date', 'freeze_count',
            'is_expired', 'days_until_renewal'
        ]
        read_only_fields = ['id', 'start_date']

    def get_owner_name(self, obj):
        """Get owner's full name"""
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip()

    def get_is_expired(self, obj):
        """Check if membership is expired"""
        return obj.renewal_date < timezone.now().date()

    def get_days_until_renewal(self, obj):
        """Get days until renewal"""
        today = timezone.now().date()
        delta = obj.renewal_date - today
        return delta.days


class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for Discount model"""

    class Meta:
        model = Discount
        fields = ['id', 'code', 'description', 'percentage', 'active']
        read_only_fields = ['id']

    def validate_code(self, value):
        """Validate discount code uniqueness"""
        if self.instance:
            if Discount.objects.filter(code__iexact=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("A discount with this code already exists.")
        else:
            if Discount.objects.filter(code__iexact=value).exists():
                raise serializers.ValidationError("A discount with this code already exists.")
        return value.upper()

    def validate_percentage(self, value):
        """Validate percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Percentage must be between 0 and 100.")
        return value


class ApplyDiscountSerializer(serializers.Serializer):
    """Serializer for applying discount codes"""
    discount_code = serializers.CharField(max_length=20)
    total_amount = serializers.DecimalField(max_digits=8, decimal_places=2)

    def validate_discount_code(self, value):
        """Validate discount code exists and is active"""
        try:
            discount = Discount.objects.get(code__iexact=value, active=True)
            return discount
        except Discount.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive discount code.")

    def validate_total_amount(self, value):
        """Validate total amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Total amount must be positive.")
        return value

    def validate(self, attrs):
        """Calculate discounted amount"""
        discount = attrs['discount_code']
        total_amount = attrs['total_amount']

        discount_amount = total_amount * (discount.percentage / 100)
        final_amount = total_amount - discount_amount

        attrs['discount_amount'] = discount_amount
        attrs['final_amount'] = final_amount
        attrs['discount_object'] = discount

        return attrs


class SessionStatsSerializer(serializers.Serializer):
    """Serializer for session statistics"""
    total_sessions = serializers.IntegerField()
    upcoming_sessions = serializers.IntegerField()
    past_sessions = serializers.IntegerField()
    full_sessions = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
