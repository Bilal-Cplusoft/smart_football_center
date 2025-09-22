from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Team
from .serializers import (
    TeamSerializer, TeamDetailSerializer, TeamListSerializer,
    TeamCreateSerializer, TeamUpdateSerializer,
    AddPlayerSerializer, RemovePlayerSerializer
)
from smart_football_center.accounts.models import User


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing teams
    """
    queryset = Team.objects.all().select_related('coach').prefetch_related('players')
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'coach__first_name', 'coach__last_name']
    ordering_fields = ['name', 'coach__first_name']
    ordering = ['name']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TeamCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TeamUpdateSerializer
        elif self.action == 'retrieve':
            return TeamDetailSerializer
        elif self.action == 'list':
            return TeamListSerializer
        return TeamSerializer

    def get_permissions(self):
        """No authentication required for any action"""
        permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        user = self.request.user
        if not user.is_authenticated:
            return Team.objects.none()

        # Admins can see all teams
        if user.role == 'admin' or user.is_staff:
            return self.queryset

        # Coaches can see teams they coach or teams with their players
        if user.role == 'coach':
            return Team.objects.filter(
                Q(coach=user) | Q(players__in=[user])
            ).distinct().select_related('coach').prefetch_related('players')

        # Players can see their teams
        if user.role in ['player', 'child']:
            return Team.objects.filter(
                players=user
            ).select_related('coach').prefetch_related('players')

        # Parents can see teams of their children (if implemented)
        return Team.objects.none()

    def perform_create(self, serializer):
        """
        Custom create logic
        """
        team = serializer.save()

        # Log team creation
        print(f"Team '{team.name}' created by user {self.request.user.username}")

    def perform_update(self, serializer):
        """
        Custom update logic
        """
        team = serializer.save()

        # Log team update
        print(f"Team '{team.name}' updated by user {self.request.user.username}")

    @action(detail=True, methods=['post'])
    def add_players(self, request, pk=None):
        """Add players to team"""
        team = self.get_object()
        serializer = AddPlayerSerializer(data=request.data)

        if serializer.is_valid():
            player_ids = serializer.validated_data['player_ids']
            players = User.objects.filter(id__in=player_ids)

            # Add players to team
            added_players = []
            for player in players:
                if not team.players.filter(id=player.id).exists():
                    team.players.add(player)
                    added_players.append(player)

            if added_players:
                player_names = [f"{p.first_name} {p.last_name}" for p in added_players]
                return Response({
                    'message': f'Added {len(added_players)} player(s) to {team.name}',
                    'added_players': player_names
                })
            else:
                return Response({
                    'message': 'All specified players were already in the team'
                })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_players(self, request, pk=None):
        """Remove players from team"""
        team = self.get_object()
        serializer = RemovePlayerSerializer(data=request.data)

        if serializer.is_valid():
            player_ids = serializer.validated_data['player_ids']
            players = User.objects.filter(id__in=player_ids)

            # Remove players from team
            removed_players = []
            for player in players:
                if team.players.filter(id=player.id).exists():
                    team.players.remove(player)
                    removed_players.append(player)

            if removed_players:
                player_names = [f"{p.first_name} {p.last_name}" for p in removed_players]
                return Response({
                    'message': f'Removed {len(removed_players)} player(s) from {team.name}',
                    'removed_players': player_names
                })
            else:
                return Response({
                    'message': 'None of the specified players were in the team'
                })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        """Get all players in the team"""
        team = self.get_object()
        from smart_football_center.accounts.serializers import UserListSerializer

        players = team.players.all().order_by('first_name', 'last_name')
        serializer = UserListSerializer(players, many=True)

        return Response({
            'team': team.name,
            'players_count': players.count(),
            'players': serializer.data
        })

    @action(detail=False, methods=['get'])
    def my_teams(self, request):
        """Get teams for the current user"""
        user = request.user

        if user.role == 'coach':
            teams = Team.objects.filter(coach=user)
            context_message = "Teams you coach"
        elif user.role in ['player', 'child']:
            teams = Team.objects.filter(players=user)
            context_message = "Teams you're a member of"
        else:
            teams = Team.objects.none()
            context_message = "No teams found"

        serializer = TeamListSerializer(teams, many=True)
        return Response({
            'message': context_message,
            'count': teams.count(),
            'teams': serializer.data
        })

    @action(detail=False, methods=['get'])
    def available_coaches(self, request):
        """Get available coaches for team assignment"""
        from smart_football_center.accounts.serializers import UserListSerializer

        coaches = User.objects.filter(
            role='coach',
            is_active=True
        ).order_by('first_name', 'last_name')

        serializer = UserListSerializer(coaches, many=True)
        return Response({
            'coaches': serializer.data
        })

    @action(detail=False, methods=['get'])
    def available_players(self, request):
        """Get available players for team assignment"""
        from smart_football_center.accounts.serializers import UserListSerializer

        players = User.objects.filter(
            role__in=['player', 'child'],
            is_active=True
        ).order_by('first_name', 'last_name')

        serializer = UserListSerializer(players, many=True)
        return Response({
            'players': serializer.data
        })

    @action(detail=True, methods=['post'])
    def assign_coach(self, request, pk=None):
        """Assign or change team coach"""
        team = self.get_object()
        coach_id = request.data.get('coach_id')

        if coach_id is None:
            return Response(
                {'error': 'coach_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if coach_id == 0 or coach_id == '':
                # Remove coach
                old_coach = team.coach
                team.coach = None
                team.save()
                return Response({
                    'message': f'Coach removed from team {team.name}',
                    'previous_coach': f"{old_coach.first_name} {old_coach.last_name}" if old_coach else None
                })
            else:
                # Assign new coach
                coach = User.objects.get(id=coach_id, role='coach', is_active=True)
                old_coach = team.coach
                team.coach = coach
                team.save()

                return Response({
                    'message': f'Coach assigned to team {team.name}',
                    'new_coach': f"{coach.first_name} {coach.last_name}",
                    'previous_coach': f"{old_coach.first_name} {old_coach.last_name}" if old_coach else None
                })

        except User.DoesNotExist:
            return Response(
                {'error': 'Coach not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get team statistics"""
        total_teams = Team.objects.count()
        teams_with_coach = Team.objects.filter(coach__isnull=False).count()
        teams_without_coach = total_teams - teams_with_coach

        # Teams by player count
        team_player_counts = []
        for team in Team.objects.all():
            team_player_counts.append({
                'team': team.name,
                'players_count': team.players.count(),
                'coach': f"{team.coach.first_name} {team.coach.last_name}" if team.coach else "No Coach"
            })

        return Response({
            'total_teams': total_teams,
            'teams_with_coach': teams_with_coach,
            'teams_without_coach': teams_without_coach,
            'team_details': team_player_counts
        })
