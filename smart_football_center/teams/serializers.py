from rest_framework import serializers
from .models import Team
from smart_football_center.accounts.serializers import UserListSerializer


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model with all details"""
    coach_name = serializers.SerializerMethodField()
    players_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'coach', 'coach_name', 'players_count']
        read_only_fields = ['id']

    def get_coach_name(self, obj):
        """Get coach's full name"""
        if obj.coach:
            return f"{obj.coach.first_name} {obj.coach.last_name}".strip()
        return None

    def get_players_count(self, obj):
        """Get number of players in the team"""
        return obj.players.count()


class TeamDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Team with nested relationships"""
    coach = UserListSerializer(read_only=True)
    players = UserListSerializer(many=True, read_only=True)
    coach_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'coach', 'coach_id', 'players']
        read_only_fields = ['id']

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
        """Create team with coach assignment"""
        coach_id = validated_data.pop('coach_id', None)
        team = Team.objects.create(**validated_data)

        if coach_id:
            from smart_football_center.accounts.models import User
            coach = User.objects.get(id=coach_id)
            team.coach = coach
            team.save()

        return team

    def update(self, instance, validated_data):
        """Update team with coach assignment"""
        coach_id = validated_data.pop('coach_id', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update coach if provided
        if coach_id is not None:
            if coach_id:
                from smart_football_center.accounts.models import User
                coach = User.objects.get(id=coach_id)
                instance.coach = coach
            else:
                instance.coach = None

        instance.save()
        return instance


class TeamListSerializer(serializers.ModelSerializer):
    """Simplified serializer for team lists"""
    coach_name = serializers.SerializerMethodField()
    players_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'coach_name', 'players_count']

    def get_coach_name(self, obj):
        """Get coach's full name"""
        if obj.coach:
            return f"{obj.coach.first_name} {obj.coach.last_name}".strip()
        return "No Coach Assigned"

    def get_players_count(self, obj):
        """Get number of players in the team"""
        return obj.players.count()


class TeamCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating teams"""
    coach_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Team
        fields = ['name', 'coach_id']

    def validate_name(self, value):
        """Validate team name uniqueness"""
        if Team.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A team with this name already exists.")
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
        """Create team with coach assignment"""
        coach_id = validated_data.pop('coach_id', None)
        team = Team.objects.create(**validated_data)

        if coach_id:
            from smart_football_center.accounts.models import User
            coach = User.objects.get(id=coach_id)
            team.coach = coach
            team.save()

        return team


class TeamUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating teams"""
    coach_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Team
        fields = ['name', 'coach_id']

    def validate_name(self, value):
        """Validate team name uniqueness (excluding current instance)"""
        if self.instance and Team.objects.filter(name__iexact=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A team with this name already exists.")
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

    def update(self, instance, validated_data):
        """Update team with coach assignment"""
        coach_id = validated_data.pop('coach_id', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update coach if provided
        if coach_id is not None:
            if coach_id:
                from smart_football_center.accounts.models import User
                coach = User.objects.get(id=coach_id)
                instance.coach = coach
            else:
                instance.coach = None

        instance.save()
        return instance


class AddPlayerSerializer(serializers.Serializer):
    """Serializer for adding players to team"""
    player_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_player_ids(self, value):
        """Validate all players exist and have correct roles"""
        from smart_football_center.accounts.models import User

        players = User.objects.filter(id__in=value)

        if len(players) != len(value):
            raise serializers.ValidationError("One or more players not found.")

        invalid_players = players.exclude(role__in=['player', 'child'])
        if invalid_players.exists():
            names = [f"{p.first_name} {p.last_name}" for p in invalid_players]
            raise serializers.ValidationError(f"These users are not players: {', '.join(names)}")

        inactive_players = players.filter(is_active=False)
        if inactive_players.exists():
            names = [f"{p.first_name} {p.last_name}" for p in inactive_players]
            raise serializers.ValidationError(f"These players are inactive: {', '.join(names)}")

        return value


class RemovePlayerSerializer(serializers.Serializer):
    """Serializer for removing players from team"""
    player_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_player_ids(self, value):
        """Validate all players exist"""
        from smart_football_center.accounts.models import User

        players = User.objects.filter(id__in=value)

        if len(players) != len(value):
            raise serializers.ValidationError("One or more players not found.")

        return value
