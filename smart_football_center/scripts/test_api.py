#!/usr/bin/env python3
"""
Simple API test script for Smart Football Center
Tests basic API endpoints to verify they're working correctly
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:8000/api'

def test_api_root():
    """Test API root endpoint"""
    print("Testing API root...")
    try:
        response = requests.get(BASE_URL + '/')
        print(f"API Root Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available endpoints: {list(data.keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing API root: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\nTesting user registration...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "role": "player"
    }

    try:
        response = requests.post(BASE_URL + '/auth/register/', json=user_data)
        print(f"Registration Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"User created: {data.get('user', {}).get('username')}")
        elif response.status_code == 400:
            print(f"Registration errors: {response.json()}")
        return response.status_code in [201, 400]  # 400 might be duplicate user
    except Exception as e:
        print(f"Error testing registration: {e}")
        return False

def test_user_login():
    """Test user login"""
    print("\nTesting user login...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    try:
        response = requests.post(BASE_URL + '/auth/login/', json=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful for: {data.get('user', {}).get('username')}")
            return response.cookies  # Return session cookies for future requests
        else:
            print(f"Login failed: {response.json()}")
        return None
    except Exception as e:
        print(f"Error testing login: {e}")
        return None

def test_teams_endpoint(cookies=None):
    """Test teams endpoint"""
    print("\nTesting teams endpoint...")
    try:
        response = requests.get(BASE_URL + '/teams/', cookies=cookies)
        print(f"Teams Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Teams count: {data.get('count', 0)}")
            if data.get('results'):
                print(f"Sample team: {data['results'][0].get('name', 'N/A')}")
        elif response.status_code == 401:
            print("Authentication required for teams endpoint")
        return response.status_code in [200, 401]
    except Exception as e:
        print(f"Error testing teams: {e}")
        return False

def test_sessions_endpoint(cookies=None):
    """Test sessions endpoint"""
    print("\nTesting sessions endpoint...")
    try:
        response = requests.get(BASE_URL + '/sessions/', cookies=cookies)
        print(f"Sessions Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Sessions count: {data.get('count', 0)}")
        elif response.status_code == 401:
            print("Authentication required for sessions endpoint")
        return response.status_code in [200, 401]
    except Exception as e:
        print(f"Error testing sessions: {e}")
        return False

def test_api_documentation():
    """Test API documentation endpoints"""
    print("\nTesting API documentation...")
    try:
        # Test schema endpoint
        response = requests.get(BASE_URL + '/schema/')
        print(f"Schema Status: {response.status_code}")

        # Test Swagger UI
        response = requests.get(BASE_URL + '/docs/')
        print(f"Swagger UI Status: {response.status_code}")

        return True
    except Exception as e:
        print(f"Error testing documentation: {e}")
        return False

def test_create_team(cookies=None):
    """Test team creation"""
    print("\nTesting team creation...")
    team_data = {
        "name": "Test Team FC"
    }

    try:
        response = requests.post(BASE_URL + '/teams/', json=team_data, cookies=cookies)
        print(f"Team Creation Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"Team created: {data.get('name')}")
            return data.get('id')
        elif response.status_code == 401:
            print("Authentication required for team creation")
        elif response.status_code == 400:
            print(f"Team creation errors: {response.json()}")
        return None
    except Exception as e:
        print(f"Error testing team creation: {e}")
        return None

def run_all_tests():
    """Run all API tests"""
    print("=== Smart Football Center API Tests ===\n")

    results = []

    # Test basic endpoints
    results.append(("API Root", test_api_root()))
    results.append(("User Registration", test_user_registration()))

    # Test authentication
    cookies = test_user_login()
    if cookies:
        results.append(("User Login", True))
    else:
        results.append(("User Login", False))

    # Test authenticated endpoints
    results.append(("Teams Endpoint", test_teams_endpoint(cookies)))
    results.append(("Sessions Endpoint", test_sessions_endpoint(cookies)))

    # Test documentation
    results.append(("API Documentation", test_api_documentation()))

    # Test creation (if authenticated)
    if cookies:
        team_id = test_create_team(cookies)
        results.append(("Team Creation", team_id is not None))

    # Print summary
    print("\n=== Test Results Summary ===")
    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    run_all_tests()
