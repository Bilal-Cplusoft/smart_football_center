#!/usr/bin/env python3
"""
Setup script to create initial test data for Smart Football Center
Run this after migrations to populate the database with sample data
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_football_center.settings')
django.setup()

from smart_football_center.accounts.models import User
from smart_football_center.teams.models import Team
from smart_football_center.bookings.models import Session, Booking, Bundle, Membership, Discount


def create_users():
    """Create sample users with different roles"""
    print("Creating users...")

    users_data = [
        {
            'username': 'admin',
            'email': 'admin@footballcenter.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'coach_john',
            'email': 'john.coach@footballcenter.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'role': 'coach',
            'phone': '+1234567890',
        },
        {
            'username': 'coach_mary',
            'email': 'mary.coach@footballcenter.com',
            'first_name': 'Mary',
            'last_name': 'Johnson',
            'role': 'coach',
            'phone': '+1234567891',
        },
        {
            'username': 'player1',
            'email': 'alex.player@example.com',
            'first_name': 'Alex',
            'last_name': 'Wilson',
            'role': 'player',
            'birth_date': '1995-03-15',
        },
        {
            'username': 'player2',
            'email': 'sarah.player@example.com',
            'first_name': 'Sarah',
            'last_name': 'Davis',
            'role': 'player',
            'birth_date': '1992-07-22',
        },
        {
            'username': 'player3',
            'email': 'mike.player@example.com',
            'first_name': 'Mike',
            'last_name': 'Brown',
            'role': 'player',
            'birth_date': '1998-11-08',
        },
        {
            'username': 'child1',
            'email': 'parent1@example.com',
            'first_name': 'Emma',
            'last_name': 'Taylor',
            'role': 'child',
            'birth_date': '2010-05-12',
        },
        {
            'username': 'child2',
            'email': 'parent2@example.com',
            'first_name': 'Lucas',
            'last_name': 'Anderson',
            'role': 'child',
            'birth_date': '2012-09-03',
        },
        {
            'username': 'parent1',
            'email': 'parent1@example.com',
            'first_name': 'Robert',
            'last_name': 'Taylor',
            'role': 'parent',
        },
    ]

    created_users = {}

    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')  # Default password for all test users
            user.save()
            print(f"  Created user: {user.username} ({user.role})")
        else:
            print(f"  User already exists: {user.username}")

        created_users[user_data['username']] = user

    return created_users


def create_teams(users):
    """Create sample teams"""
    print("Creating teams...")

    teams_data = [
        {
            'name': 'Arsenal FC',
            'coach': users['coach_john'],
            'players': ['player1', 'player2', 'child1']
        },
        {
            'name': 'Chelsea United',
            'coach': users['coach_mary'],
            'players': ['player3', 'child2']
        },
        {
            'name': 'Liverpool Stars',
            'coach': None,
            'players': ['player1', 'player3']
        },
    ]

    created_teams = {}

    for team_data in teams_data:
        team, created = Team.objects.get_or_create(
            name=team_data['name'],
            defaults={'coach': team_data['coach']}
        )

        if created:
            # Add players to team
            for player_username in team_data['players']:
                if player_username in users:
                    team.players.add(users[player_username])
            print(f"  Created team: {team.name} (Coach: {team.coach.first_name if team.coach else 'None'})")
        else:
            print(f"  Team already exists: {team.name}")

        created_teams[team_data['name']] = team

    return created_teams


def create_sessions(users):
    """Create sample training sessions"""
    print("Creating sessions...")

    now = timezone.now()

    sessions_data = [
        {
            'name': 'Morning Training Session',
            'session_type': 'group',
            'coach': users['coach_john'],
            'date': now + timedelta(days=1, hours=9),
            'duration_minutes': 90,
            'price': 25.00,
            'capacity': 15,
            'spots_left': 12,
        },
        {
            'name': '1-on-1 Skill Development',
            'session_type': '1on1',
            'coach': users['coach_mary'],
            'date': now + timedelta(days=2, hours=14),
            'duration_minutes': 60,
            'price': 80.00,
            'capacity': 1,
            'spots_left': 1,
        },
        {
            'name': 'Youth Training Camp',
            'session_type': 'event',
            'coach': users['coach_john'],
            'date': now + timedelta(days=5, hours=10),
            'duration_minutes': 180,
            'price': 50.00,
            'capacity': 20,
            'spots_left': 18,
        },
        {
            'name': 'Recovery Session',
            'session_type': 'recovery',
            'coach': users['coach_mary'],
            'date': now + timedelta(days=3, hours=16),
            'duration_minutes': 45,
            'price': 15.00,
            'capacity': 10,
            'spots_left': 8,
        },
        {
            'name': 'Evening Group Training',
            'session_type': 'group',
            'coach': users['coach_john'],
            'date': now + timedelta(days=7, hours=18),
            'duration_minutes': 120,
            'price': 30.00,
            'capacity': 12,
            'spots_left': 10,
        },
    ]

    created_sessions = {}

    for session_data in sessions_data:
        session, created = Session.objects.get_or_create(
            name=session_data['name'],
            date=session_data['date'],
            defaults=session_data
        )

        if created:
            print(f"  Created session: {session.name} ({session.date.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"  Session already exists: {session.name}")

        created_sessions[session_data['name']] = session

    return created_sessions


def create_bookings(users, sessions):
    """Create sample bookings"""
    print("Creating bookings...")

    bookings_data = [
        {
            'player': users['player1'],
            'session': sessions['Morning Training Session'],
            'status': 'confirmed'
        },
        {
            'player': users['player2'],
            'session': sessions['Morning Training Session'],
            'status': 'confirmed'
        },
        {
            'player': users['child1'],
            'session': sessions['Youth Training Camp'],
            'status': 'confirmed'
        },
        {
            'player': users['player3'],
            'session': sessions['Recovery Session'],
            'status': 'confirmed'
        },
    ]

    for booking_data in bookings_data:
        booking, created = Booking.objects.get_or_create(
            player=booking_data['player'],
            session=booking_data['session'],
            defaults={'status': booking_data['status']}
        )

        if created:
            # Update session spots
            session = booking_data['session']
            session.spots_left = max(0, session.spots_left - 1)
            session.save()
            print(f"  Created booking: {booking.player.first_name} -> {booking.session.name}")
        else:
            print(f"  Booking already exists: {booking.player.first_name} -> {booking.session.name}")


def create_bundles(users):
    """Create sample bundles"""
    print("Creating bundles...")

    bundles_data = [
        {
            'owner': users['player1'],
            'sessions_included': 10,
            'sessions_used': 2,
            'expiry_date': timezone.now().date() + timedelta(days=90),
        },
        {
            'owner': users['player2'],
            'sessions_included': 5,
            'sessions_used': 0,
            'expiry_date': timezone.now().date() + timedelta(days=60),
        },
    ]

    for bundle_data in bundles_data:
        bundle, created = Bundle.objects.get_or_create(
            owner=bundle_data['owner'],
            sessions_included=bundle_data['sessions_included'],
            defaults=bundle_data
        )

        if created:
            print(f"  Created bundle: {bundle.owner.first_name} - {bundle.sessions_included} sessions")
        else:
            print(f"  Bundle already exists for: {bundle.owner.first_name}")


def create_memberships(users):
    """Create sample memberships"""
    print("Creating memberships...")

    memberships_data = [
        {
            'owner': users['player1'],
            'active': True,
            'plan_name': 'Premium Monthly',
            'renewal_date': timezone.now().date() + timedelta(days=30),
            'freeze_count': 0,
        },
        {
            'owner': users['player2'],
            'active': True,
            'plan_name': 'Basic Monthly',
            'renewal_date': timezone.now().date() + timedelta(days=25),
            'freeze_count': 1,
        },
        {
            'owner': users['child1'],
            'active': True,
            'plan_name': 'Youth Plan',
            'renewal_date': timezone.now().date() + timedelta(days=40),
            'freeze_count': 0,
        },
    ]

    for membership_data in memberships_data:
        membership, created = Membership.objects.get_or_create(
            owner=membership_data['owner'],
            plan_name=membership_data['plan_name'],
            defaults=membership_data
        )

        if created:
            print(f"  Created membership: {membership.owner.first_name} - {membership.plan_name}")
        else:
            print(f"  Membership already exists for: {membership.owner.first_name}")


def create_discounts():
    """Create sample discount codes"""
    print("Creating discounts...")

    discounts_data = [
        {
            'code': 'WELCOME10',
            'description': '10% off for new members',
            'percentage': 10,
            'active': True,
        },
        {
            'code': 'STUDENT20',
            'description': '20% student discount',
            'percentage': 20,
            'active': True,
        },
        {
            'code': 'FAMILY15',
            'description': '15% family discount',
            'percentage': 15,
            'active': True,
        },
        {
            'code': 'EXPIRED50',
            'description': 'Expired 50% discount',
            'percentage': 50,
            'active': False,
        },
    ]

    for discount_data in discounts_data:
        discount, created = Discount.objects.get_or_create(
            code=discount_data['code'],
            defaults=discount_data
        )

        if created:
            print(f"  Created discount: {discount.code} ({discount.percentage}% off)")
        else:
            print(f"  Discount already exists: {discount.code}")


def main():
    """Main setup function"""
    print("=== Setting up test data for Smart Football Center ===\n")

    try:
        # Create users
        users = create_users()

        # Create teams
        teams = create_teams(users)

        # Create sessions
        sessions = create_sessions(users)

        # Create bookings
        create_bookings(users, sessions)

        # Create bundles
        create_bundles(users)

        # Create memberships
        create_memberships(users)

        # Create discounts
        create_discounts()

        print("\n=== Test data setup completed successfully! ===")
        print("\nDefault login credentials:")
        print("Admin: admin / password123")
        print("Coach: coach_john / password123")
        print("Player: player1 / password123")
        print("\nYou can now test the API with these users and data.")

    except Exception as e:
        print(f"\nError setting up test data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
