#!/usr/bin/env python3
"""
Test script for RBAC (Role-Based Access Control).
Tests that endpoints are properly protected by role requirements.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
BUSINESS_ID = "dc33f1dc-7fca-4628-bd75-e8b6eb6d8ca6"


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


def test_public_registration_with_admin_role():
    """Test that public registration rejects non-CUSTOMER roles."""
    url = f"{BASE_URL}/auth/register"
    payload = {
        "email": "hacker@test.com",
        "password": "password123",
        "name": "Hacker",
        "phone": "1234567890",
        "address": "123 Hack St",
        "businessId": BUSINESS_ID,
        "role": "SUPER_ADMIN",  # Try to register as admin
    }

    response = requests.post(url, json=payload)
    print_response(response, "TEST: Public Registration with SUPER_ADMIN Role (Should Fail)")
    return response.status_code == 400


def test_customer_cannot_create_tag_mapping(customer_token: str):
    """Test that customers cannot create tag mappings."""
    url = f"{BASE_URL}/tag-mapping/create"
    headers = {"Authorization": f"Bearer {customer_token}"}
    payload = {"epc": "E2806810000000001234TEST", "product_id": None, "container_id": None}

    response = requests.post(url, json=payload, headers=headers)
    print_response(response, "TEST: Customer Creating Tag Mapping (Should Fail - 403)")
    return response.status_code == 403


def test_customer_cannot_delete_tag_mapping(customer_token: str):
    """Test that customers cannot delete tag mappings."""
    url = f"{BASE_URL}/tag-mapping/fake-id-12345"
    headers = {"Authorization": f"Bearer {customer_token}"}

    response = requests.delete(url, headers=headers)
    print_response(response, "TEST: Customer Deleting Tag Mapping (Should Fail - 403)")
    return response.status_code == 403


def main():
    """Run all RBAC tests."""
    print("\n" + "=" * 60)
    print("RBAC (ROLE-BASED ACCESS CONTROL) TESTS")
    print("=" * 60)

    results = []

    # Test 1: Public registration with admin role
    print("\n\n### TEST 1: Prevent Admin Role in Public Registration ###")
    results.append(
        ("Public registration blocks admin roles", test_public_registration_with_admin_role())
    )

    # Test 2: Register a customer to get a token
    print("\n\n### TEST 2: Register Customer for Testing ###")
    url = f"{BASE_URL}/auth/register"
    payload = {
        "email": f"rbac_test_{hash('test')}@test.com",
        "password": "password123",
        "name": "RBAC Test Customer",
        "phone": "1234567890",
        "address": "123 Test St",
        "businessId": BUSINESS_ID,
        "role": "CUSTOMER",
    }

    response = requests.post(url, json=payload)
    print_response(response, "Register Customer")

    if response.status_code == 201:
        customer_token = response.json().get("token")

        # Test 3: Customer cannot create tag mappings
        print("\n\n### TEST 3: Customer Cannot Create Tag Mappings ###")
        results.append(
            (
                "Customer blocked from creating tag mappings",
                test_customer_cannot_create_tag_mapping(customer_token),
            )
        )

        # Test 4: Customer cannot delete tag mappings
        print("\n\n### TEST 4: Customer Cannot Delete Tag Mappings ###")
        results.append(
            (
                "Customer blocked from deleting tag mappings",
                test_customer_cannot_delete_tag_mapping(customer_token),
            )
        )
    else:
        print("⚠️ Could not register customer, skipping remaining tests")

    # Summary
    print("\n\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
