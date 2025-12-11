#!/usr/bin/env python3
"""
Test suite for Phase 3: Plan Revision API

Tests the skeleton /api/v1/revise_plan endpoint.
"""

import requests
import sys

# API configuration
API_BASE = "http://127.0.0.1:8002"


def test_revise_plan_basic():
    """Test 1: /api/v1/revise_plan returns success and echoes plan."""
    print("\n[TEST 1] Basic revise_plan endpoint test")
    print("-" * 60)

    payload = {
        "old_plan": [
            {"id": 1, "action": "click", "params": {"target": "btn_filter"}},
            {"id": 2, "action": "input", "params": {"field": "amount", "value": "1000"}},
        ],
        "user_feedback": "違う、この列じゃなくて税込金額でフィルタして",
    }

    try:
        resp = requests.post(
            f"{API_BASE}/api/v1/revise_plan",
            json=payload,
            timeout=10
        )

        print(f"Status Code: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[FAIL] - Expected 200, got {resp.status_code}")
            print(f"Response: {resp.text}")
            return False

        data = resp.json()
        print(f"Response: {data}")

        # Validate response structure
        assert data["success"] is True, "Expected success: true"
        assert len(data["revised_plan"]) == 2, "Expected 2 steps in revised_plan"
        assert "message" in data, "Expected 'message' field in response"
        assert "stub" in data["message"].lower(), "Expected stub indication in message"

        # Verify plan structure
        for step in data["revised_plan"]:
            assert "action" in step, "Each step must have 'action'"
            assert "params" in step, "Each step must have 'params'"

        print("[PASS] - Basic endpoint test passed")
        return True

    except requests.exceptions.ConnectionError:
        print("[FAIL] - Could not connect to server")
        print(f"Make sure server is running on {API_BASE}")
        return False
    except Exception as e:
        print(f"[FAIL] - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_revise_plan_with_optional_fields():
    """Test 2: /api/v1/revise_plan with optional fields."""
    print("\n[TEST 2] Revise plan with optional fields")
    print("-" * 60)

    payload = {
        "old_plan": [
            {"action": "navigate", "params": {"url": "https://example.com"}},
        ],
        "user_feedback": "先にログインしてから",
        "screen_description": "Login page with username and password fields",
        "session_id": "test-session-123"
    }

    try:
        resp = requests.post(
            f"{API_BASE}/api/v1/revise_plan",
            json=payload,
            timeout=10
        )

        print(f"Status Code: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[FAIL] - Expected 200, got {resp.status_code}")
            return False

        data = resp.json()
        assert data["success"] is True
        assert len(data["revised_plan"]) == 1

        print("[PASS] - Optional fields handled correctly")
        return True

    except Exception as e:
        print(f"[FAIL] - {str(e)}")
        return False


def test_revise_plan_empty_plan():
    """Test 3: /api/v1/revise_plan with empty plan."""
    print("\n[TEST 3] Revise plan with empty plan")
    print("-" * 60)

    payload = {
        "old_plan": [],
        "user_feedback": "Add a step to click the button",
    }

    try:
        resp = requests.post(
            f"{API_BASE}/api/v1/revise_plan",
            json=payload,
            timeout=10
        )

        print(f"Status Code: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[FAIL] - Expected 200, got {resp.status_code}")
            return False

        data = resp.json()
        assert data["success"] is True
        assert len(data["revised_plan"]) == 0  # Stub returns empty plan as-is

        print("[PASS] - Empty plan handled correctly")
        return True

    except Exception as e:
        print(f"[FAIL] - {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 3: PLAN REVISION API TEST SUITE")
    print("=" * 60)

    tests = [
        test_revise_plan_basic,
        test_revise_plan_with_optional_fields,
        test_revise_plan_empty_plan,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Test {test_func.__name__} crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {total - passed} TEST(S) FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
