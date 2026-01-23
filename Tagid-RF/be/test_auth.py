#!/usr/bin/env python3
"""
Test script for authentication endpoints.
Tests registration, login, and user management.
"""

import json
from typing import Optional

import requests

BASE_URL = "http://localhost:8000/api/v1"
BUSINESS_ID = "dc33f1dc-7fca-4628-bd75-e8b6eb6d8ca6"  # From setup_test_data.py


def print_response(response: requests.Response, title: str):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_register(
    email: str, password: str, name: str, business_id: str, role: str = "CUSTOMER"
) -> Optional[dict]:
    """Test user registration."""
    url = f"{BASE_URL}/auth/register"
    payload = {
        "email": email,
        "password": password,
        "name": name,
        "phone": "1234567890",
        "address": "123 Test Street",
        "businessId": business_id,
        "role": role,
    }

    response = requests.post(url, json=payload)
    print_response(response, f"REGISTER USER: {email}")

    if response.status_code == 201:
        return response.json()
    return None


def test_login(email: str, password: str) -> Optional[str]:
    """Test user login and return token."""
    url = f"{BASE_URL}/auth/login"
    payload = {"email": email, "password": password}

    response = requests.post(url, json=payload)
    print_response(response, f"LOGIN: {email}")

    if response.status_code == 200:
        return response.json().get("token")
    return None


def test_get_me(token: str):
    """Test getting current user info."""
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print_response(response, "GET CURRENT USER (/auth/me)")


def test_create_user(token: str, email: str, role: str = "EMPLOYEE"):
    """Test creating a new user (admin only)."""
    url = f"{BASE_URL}/users/"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "email": email,
        "password": "password123",
        "name": f"Test {role}",
        "phone": "9876543210",
        "address": "456 Admin Street",
        "businessId": "test-business-123",
        "role": role,
    }

    response = requests.post(url, json=payload, headers=headers)
    print_response(response, f"CREATE USER: {email} (Role: {role})")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AUTHENTICATION SYSTEM TEST")
    print("=" * 60)

    # Test 1: Register a new customer
    print("\n\n### TEST 1: Register Customer ###")
    customer_data = test_register(
        email="customer@test.com",
        password="password123",
        name="Test Customer",
        business_id=BUSINESS_ID,
        role="CUSTOMER",
    )

    # Test 2: Login with customer credentials
    print("\n\n### TEST 2: Login as Customer ###")
    customer_token = test_login("customer@test.com", "password123")

    if customer_token:
        # Test 3: Get current user info
        print("\n\n### TEST 3: Get Current User Info ###")
        test_get_me(customer_token)

        # Test 4: Try to create user as customer (should fail)
        print("\n\n### TEST 4: Try Creating User as Customer (Should Fail) ###")
        test_create_user(customer_token, "employee@test.com", "EMPLOYEE")

    # Test 5: Register a store manager
    print("\n\n### TEST 5: Register Store Manager ###")
    manager_data = test_register(
        email="manager@test.com",
        password="password123",
        name="Test Manager",
        business_id="test-business-123",
        role="STORE_MANAGER",
    )

    # Test 6: Login as manager
    print("\n\n### TEST 6: Login as Store Manager ###")
    manager_token = test_login("manager@test.com", "password123")

    if manager_token:
        # Test 7: Create employee as manager (should succeed)
        print("\n\n### TEST 7: Create Employee as Manager (Should Succeed) ###")
        test_create_user(manager_token, "employee@test.com", "EMPLOYEE")

        # Test 8: Try to create network manager (should fail)
        print(
            "\n\n### TEST 8: Try Creating Network Manager as Store Manager (Should Fail) ###"
        )
        test_create_user(manager_token, "network@test.com", "NETWORK_MANAGER")

    # Test 9: Test wrong password
    print("\n\n### TEST 9: Login with Wrong Password (Should Fail) ###")
    test_login("customer@test.com", "wrongpassword")

    # Test 10: Test duplicate registration
    print("\n\n### TEST 10: Duplicate Registration (Should Fail) ###")
    test_register(
        email="customer@test.com",
        password="password123",
        name="Duplicate Customer",
        business_id="test-business-123",
    )

    print("\n\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
